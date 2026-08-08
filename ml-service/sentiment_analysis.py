import requests
import os
from datetime import datetime, timedelta
import feedparser
import urllib.parse
import re, html
HF_TOKEN = os.getenv('HF_TOKEN')
HF_URL = "https://router.huggingface.co/hf-inference/models/ProsusAI/finbert"
COMPANY_NAMES = {
    'AAPL': 'Apple Inc', 'MSFT': 'Microsoft', 'GOOGL': 'Alphabet',
    'TSLA': 'Tesla', 'AMZN': 'Amazon', 'META': 'Meta Platforms',
    'NVDA': 'Nvidia', 'BABA': 'Alibaba',
    'TCS.NS': 'Tata Consultancy Services', 'RELIANCE.NS': 'Reliance Industries',
    'INFY.NS': 'Infosys', 'WIPRO.NS': 'Wipro', 'HDFCBANK.NS': 'HDFC Bank',
    'BARC.L': 'Barclays', 'SHEL.L': 'Shell plc', 'SAP.DE': 'SAP SE',
    '7203.T': 'Toyota Motor', '0700.HK': 'Tencent', 'NESN.SW': 'Nestle',
}

EXCHANGE_LOCALE = {
    '.NS': 'IN', '.BO': 'IN', '.L': 'GB', '.T': 'JP', '.DE': 'DE',
    '.PA': 'FR', '.HK': 'HK', '.AX': 'AU', '.TO': 'CA', '.SW': 'CH', '.SS': 'CN',
}

QUOTE_PAGE_PATTERNS = (
    'stock price, news, quote', 'share price today', 'stock price today',
    'quote and history', 'price, quote', 'live share price',
    'stock quote price and forecast', 'earnings date and reports',
)
QUOTE_DOMAINS = ('scanx.trade', 'finance.yahoo.com/quote', 'in.investing.com/equities')
MARKETAUX_KEY = os.getenv('MARKETAUX_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

def _fetch_marketaux(ticker, days, min_score, pages=3):
    """Fetch entity-tagged articles above a relevance threshold."""
    out = []
    after = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M')
    for page in range(1, pages + 1):
        try:
            r = requests.get('https://api.marketaux.com/v1/news/all', params={
                'symbols': ticker,
                'filter_entities': 'true',
                'must_have_entities': 'true',
                'sort': 'entity_match_score',
                'language': 'en',
                'published_after': after,
                'page': page,
                'api_token': MARKETAUX_KEY,
            }, timeout=10)
            if r.status_code != 200:
                print(f"Marketaux error p{page}: {r.status_code} {r.text[:150]}")
                break
            batch = r.json().get('data', [])
            if not batch:
                break
            for a in batch:
                ents = a.get('entities') or []
                score = ents[0].get('match_score', 0) if ents else 0
                print(f"  [{score:6.1f}] {(a.get('title') or '')[:60]}")
                if score < min_score:
                    continue
                out.append({
                    'title': a.get('title'),
                    'description': a.get('description') or a.get('snippet'),
                    'url': a.get('url'),
                    'source': {'name': a.get('source')},
                    'publishedAt': a.get('published_at'),
                    'match_score': round(score, 1),
                })
        except Exception as e:
            print(f"Marketaux fetch error p{page}: {e}")
            break
    return out


def _locale_for(ticker):
    for suffix, gl in EXCHANGE_LOCALE.items():
        if ticker.endswith(suffix):
            return gl
    return 'US'


def _is_junk(title, url):
    t = (title or '').lower()
    u = (url or '').lower()
    if len(t) < 25:
        return True
    return any(p in t for p in QUOTE_PAGE_PATTERNS) or any(d in u for d in QUOTE_DOMAINS)

def _clean_summary(raw, title):
    if not raw:
        return ''
    text = re.sub(r'<[^>]+>', ' ', raw)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text or title.lower()[:40] in text.lower():
        return ''
    return text[:400]

def _fetch_gnews(ticker, company_name=None, days=14, limit=25):
    base = ticker.replace('.NS', '').replace('.BO', '')
    name = company_name or COMPANY_NAMES.get(ticker) or base
    gl = _locale_for(ticker)
    q = f'"{name}" (stock OR shares OR earnings OR revenue OR results) when:{days}d'
    url = ('https://news.google.com/rss/search?q=' + urllib.parse.quote(q)
           + f'&hl=en&gl={gl}&ceid={gl}:en')
    try:
        feed = feedparser.parse(url)
        out = []
        for e in feed.entries[:limit]:
            title = re.sub(r'\s+-\s+[^-]{2,30}$', '', e.title).strip()
            if _is_junk(title, e.link):
                continue
            out.append({
                'title': title,
                'description': _clean_summary(getattr(e, 'summary', ''), title),
                'url': e.link,
                'source': {'name': getattr(getattr(e, 'source', None), 'title', 'Google News')},
                'publishedAt': getattr(e, 'published', None),
            })
        print(f"GNews {ticker} ({gl}): {len(out)} articles")
        return out
    except Exception as ex:
        print(f"GNews error: {ex}")
        return []


def get_stock_news(ticker, company_name=None, days=None):
    pool = _fetch_gnews(ticker, company_name)
    if len(pool) < 5:
        print(f"GNews thin for {ticker}, trying Marketaux")
        pool += _fetch_marketaux(ticker, days=90, min_score=25, pages=1)

    seen, out = set(), []
    for a in pool:
        u = a.get('url')
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(a)
    print(f"get_stock_news {ticker}: {len(pool)} pooled -> {len(out)} returned")
    return out[:8]



def analyze_sentiment(text):
    """Financial sentiment via FinBERT on the HF Inference API."""
    try:
        r = requests.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": text[:1000], "options": {"wait_for_model": True}},
            timeout=30,
        )
        r.raise_for_status()
        out = r.json()

        # single input -> [[{label, score}, ...]]
        scores = out[0] if isinstance(out[0], list) else out
        best = max(scores, key=lambda s: s['score'])
        label = best['label'].lower()
        score = best['score']

        polarity = score if label == 'positive' else -score if label == 'negative' else 0.0
        return {'polarity': round(polarity, 4), 'sentiment': label}

    except Exception as e:
        print(f"FinBERT API error: {e}")
        return {'polarity': 0, 'sentiment': 'neutral'}
    
    
def analyze_sentiment_batch(texts):
    if not texts:
        return []
    return [analyze_sentiment(t) for t in texts]
    
    
def analyze_news_sentiment(ticker, company_name=None):
    try:
        articles = get_stock_news(ticker, company_name)
        print(f"analyze_news_sentiment got {len(articles)} articles")

        if not articles:
            return {
                'ticker': ticker,
                'articles_analyzed': 0,
                'overall_sentiment': 'neutral',
                'average_polarity': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'recent_articles': [],
                'message': 'No recent news articles found'
            }

        sentiments = []
        analyzed_articles = []

        batch = articles[:10]
        texts = [f"{a.get('title') or ''}. {a.get('description') or ''}".strip() for a in batch]
        batch_results = analyze_sentiment_batch(texts)

        for article, sentiment in zip(batch, batch_results):
            sentiments.append(sentiment['polarity'])
            analyzed_articles.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url'),
                'source': article.get('source', {}).get('name'),
                'published_at': article.get('publishedAt'),
                'sentiment': sentiment['sentiment'],
                'scope': article.get('scope', 'market'),
                'match_score': article.get('match_score'),
                'polarity': round(sentiment['polarity'], 3)
            })

        weights = [2.0 if a.get('scope') == 'company' else 1.0 for a in batch]
        total_w = sum(weights) or 1
        avg_polarity = sum(p * w for p, w in zip(sentiments, weights)) / total_w

        if avg_polarity > 0.1:
            overall_sentiment = 'positive'
        elif avg_polarity < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
            
        

        sentiment_counts = {
            'positive': sum(1 for s in sentiments if s > 0.1),
            'neutral': sum(1 for s in sentiments if -0.1 <= s <= 0.1),
            'negative': sum(1 for s in sentiments if s < -0.1)
        }

        return {
            'ticker': ticker,
            'articles_analyzed': len(analyzed_articles),
            'overall_sentiment': overall_sentiment,
            'average_polarity': round(avg_polarity, 3),
            'sentiment_distribution': sentiment_counts,
            'recent_articles': analyzed_articles
        }

    except Exception as e:
        raise Exception(f"News sentiment analysis failed: {str(e)}")

def generate_recommendation(prediction_data, sentiment_data):
    try:
        predicted_change = prediction_data.get('percent_change', 0)
        r2_score = prediction_data.get('r2_score', 0)
        sentiment = sentiment_data.get('overall_sentiment', 'neutral')
        avg_polarity = sentiment_data.get('average_polarity', 0)
        
        score = 0
        reasons = []
        
        if predicted_change > 2:
            score += 40
            reasons.append(f"Strong predicted price increase ({predicted_change:.2f}%)")
        elif predicted_change > 0:
            score += 20
            reasons.append(f"Modest predicted price increase ({predicted_change:.2f}%)")
        elif predicted_change > -2:
            score -= 10
            reasons.append(f"Slight predicted price decrease ({predicted_change:.2f}%)")
        else:
            score -= 30
            reasons.append(f"Significant predicted price decrease ({predicted_change:.2f}%)")
        
        if r2_score > 0.95:
            score += 20
            reasons.append(f"High model confidence (R² = {r2_score:.3f})")
        elif r2_score > 0.85:
            score += 10
            reasons.append(f"Good model confidence (R² = {r2_score:.3f})")
        else:
            score -= 5
            reasons.append(f"Moderate model confidence (R² = {r2_score:.3f})")
        
        if sentiment == 'positive' and avg_polarity > 0.2:
            score += 40
            reasons.append(f"Strong positive news sentiment (polarity: {avg_polarity:.3f})")
        elif sentiment == 'positive':
            score += 25
            reasons.append(f"Positive news sentiment (polarity: {avg_polarity:.3f})")
        elif sentiment == 'neutral':
            score += 10
            reasons.append(f"Neutral news sentiment (polarity: {avg_polarity:.3f})")
        elif sentiment == 'negative' and avg_polarity < -0.2:
            score -= 40
            reasons.append(f"Strong negative news sentiment (polarity: {avg_polarity:.3f})")
        else:
            score -= 20
            reasons.append(f"Negative news sentiment (polarity: {avg_polarity:.3f})")
        
        if score >= 60:
            recommendation = 'Strong Buy'
            action = 'BUY'
            confidence = 'High'
        elif score >= 30:
            recommendation = 'Buy'
            action = 'BUY'
            confidence = 'Medium'
        elif score >= 10:
            recommendation = 'Hold'
            action = 'HOLD'
            confidence = 'Medium'
        elif score >= -20:
            recommendation = 'Sell'
            action = 'SELL'
            confidence = 'Medium'
        else:
            recommendation = 'Strong Sell'
            action = 'SELL'
            confidence = 'High'
        
        return {
            'recommendation': recommendation,
            'action': action,
            'confidence': confidence,
            'score': score,
            'reasons': reasons,
            'disclaimer': 'This recommendation is generated by an AI model and should not be considered as financial advice. Always do your own research and consult with a financial advisor before making investment decisions.'
        }
        
    except Exception as e:
        raise Exception(f"Recommendation generation failed: {str(e)}")
