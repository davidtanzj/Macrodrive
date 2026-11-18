SOURCES = [

    # ========================================================
    # FEDERAL RESERVE
    # ========================================================

    {
        "name": "Federal Reserve",
        "type": "rss",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # ========================================================
    # EIA
    # ========================================================

    {
        "name": "EIA",
        "type": "rss",
        "url": "https://www.eia.gov/rss/todayinenergy.xml",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # ========================================================
    # BIS
    # ========================================================

    {
        "name": "BIS Research",
        "type": "rss",
        "url": "https://www.bis.org/doclist/bis_fsi_publs.rss",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    {
        "name": "BIS Central Bank Speeches",
        "type": "rss",
        "url": "https://www.bis.org/doclist/cbspeeches.rss",
        "max_articles": 30,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    {
        "name": "BIS Press Releases",
        "type": "rss",
        "url": "https://www.bis.org/doclist/all_pressrels.rss",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # ========================================================
    # WORLD BANK
    # ========================================================

    {
        "name": "World Bank",
        "type": "worldbank_api",
        "url": "https://search.worldbank.org/api/v2/news",
        "max_articles": 20,
        "text_mode": "provided",
        "access_type": "free",
        "enabled": True
    },

    # ========================================================
    # IMF BLOG
    # Currently disabled because automated requests return 403.
    # ========================================================

    {
        "name": "IMF Blog",
        "type": "imf_blog",
        "url": "https://www.imf.org/en/blogs",
        "max_articles": 20,
        "text_mode": "provided",
        "access_type": "free",
        "enabled": False
    },

    # ========================================================
    # BUSINESS TIMES
    # Mixed access.
    # ========================================================

    {
        "name": "Business Times",
        "type": "rss",
        "url": "https://www.businesstimes.com.sg/rss/economy-policy",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "Business Times",
        "type": "rss",
        "url": "https://www.businesstimes.com.sg/rss/international",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "Business Times",
        "type": "rss",
        "url": "https://www.businesstimes.com.sg/rss/energy-commodities",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "Business Times",
        "type": "rss",
        "url": "https://www.businesstimes.com.sg/rss/capital-markets-currencies",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    # ========================================================
    # SOUTH CHINA MORNING POST
    # Mixed access.
    # ========================================================

    {
        "name": "South China Morning Post",
        "type": "rss",
        "url": "https://www.scmp.com/rss/4/feed",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "South China Morning Post",
        "type": "rss",
        "url": "https://www.scmp.com/rss/92/feed",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "South China Morning Post",
        "type": "rss",
        "url": "https://www.scmp.com/rss/7/feed",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    # ========================================================
    # BLOOMBERG
    # Public author RSS metadata only.
    # ========================================================

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/ABoevEwlk2U/michael-mckee.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/ADOQshTSiRE/cynthia-li.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/ATnBsaGsPW8/claire-jiao.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/AG-IhEh0UAE/malcolm-scott.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/APgqIL003O8/jana-randow.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/AV1oOPlc7hY/julian-harris.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/AWqWk4pq2Wg/mark-schroers.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    {
        "name": "Bloomberg",
        "type": "rss",
        "url": "https://www.bloomberg.com/authors/AQug5IYzEQE/james-mayger.rss",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "enabled": True
    },

    # ========================================================
    # WALL STREET JOURNAL
    # Public Dow Jones RSS metadata only.
    # ========================================================

    {
        "name": "Wall Street Journal",
        "type": "rss",
        "url": "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
        "max_articles": 30,
        "text_mode": "metadata_only",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "Wall Street Journal",
        "type": "rss",
        "url": "https://feeds.content.dowjones.io/public/rss/RSSWorldNews",
        "max_articles": 30,
        "text_mode": "metadata_only",
        "access_type": "unknown",
        "enabled": True
    },

    # ========================================================
    # FINANCIAL TIMES
    # Public FT RSS metadata only.
    # ========================================================

    {
        "name": "Financial Times",
        "type": "rss",
        "url": "https://www.ft.com/global-economy?format=rss",
        "max_articles": 30,
        "text_mode": "metadata_only",
        "access_type": "unknown",
        "enabled": True
    },

    {
        "name": "Financial Times",
        "type": "rss",
        "url": "https://www.ft.com/markets?format=rss",
        "max_articles": 30,
        "text_mode": "metadata_only",
        "access_type": "unknown",
        "enabled": True
    },

    # ========================================================
    # CNBC
    #
    # Public RSS feeds. Article access will be determined
    # individually by the normal text/access processing.
    # ========================================================

    # Economy
    {
        "name": "CNBC",
        "type": "rss",
        "url": "https://www.cnbc.com/id/20910258/device/rss/rss.html",
        "max_articles": 30,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    # Finance
    {
        "name": "CNBC",
        "type": "rss",
        "url": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "max_articles": 30,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    # Energy
    {
        "name": "CNBC",
        "type": "rss",
        "url": "https://www.cnbc.com/id/19836768/device/rss/rss.html",
        "max_articles": 30,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    },

    # Asia
    {
        "name": "CNBC",
        "type": "rss",
        "url": "https://www.cnbc.com/id/19832390/device/rss/rss.html",
        "max_articles": 30,
        "text_mode": "full",
        "access_type": "unknown",
        "enabled": True
    }


,
    # EUROPEAN CENTRAL BANK
    {
        "name": "European Central Bank",
        "type": "rss",
        "url": "https://www.ecb.europa.eu/rss/press.html",
        "max_articles": 25,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },
    {
        "name": "European Central Bank",
        "type": "rss",
        "url": "https://www.ecb.europa.eu/rss/key.html",
        "max_articles": 25,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # BANK OF ENGLAND
    {
        "name": "Bank of England",
        "type": "rss",
        "url": "https://www.bankofengland.co.uk/rss/news",
        "max_articles": 25,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },
    {
        "name": "Bank of England",
        "type": "rss",
        "url": "https://www.bankofengland.co.uk/rss/speeches",
        "max_articles": 25,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # RESERVE BANK OF AUSTRALIA
    {
        "name": "Reserve Bank of Australia",
        "type": "rss",
        "url": "https://www.rba.gov.au/rss/rss-cb-media-releases.xml",
        "max_articles": 25,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },
    {
        "name": "Reserve Bank of Australia",
        "type": "rss",
        "url": "https://www.rba.gov.au/rss/rss-cb-speeches.xml",
        "max_articles": 25,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # BANK OF CANADA
    {
        "name": "Bank of Canada",
        "type": "rss",
        "url": "https://www.bankofcanada.ca/feed/",
        "max_articles": 30,
        "text_mode": "full",
        "access_type": "free",
        "enabled": True
    },

    # ========================================================
    # ASIA — NEWS SOURCES
    # The `region` key is reference metadata only; article region
    # tagging is done at runtime by regiondetector.py (content-based).
    # ========================================================

    # Nikkei Asia — hard paywall, metadata only.
    {
        "name": "Nikkei Asia",
        "type": "rss",
        "url": "https://asia.nikkei.com/rss/feed/nar",
        "max_articles": 20,
        "text_mode": "metadata_only",
        "access_type": "paywalled",
        "region": "Asia",
        "enabled": True
    },

    # Mint (India) — free, full text.
    {
        "name": "Mint",
        "type": "rss",
        "url": "https://www.livemint.com/rss/markets",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "region": "Asia",
        "enabled": True
    },
    {
        "name": "Mint",
        "type": "rss",
        "url": "https://www.livemint.com/rss/money",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "region": "Asia",
        "enabled": True
    },

    # Economic Times (India) — economy, free, full text.
    {
        "name": "Economic Times",
        "type": "rss",
        "url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "region": "Asia",
        "enabled": True
    },

    # Yonhap (South Korea) — economy & finance, free, full text.
    {
        "name": "Yonhap",
        "type": "rss",
        "url": "https://en.yna.co.kr/RSS/economy-finance.xml",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "unknown",
        "region": "Asia",
        "enabled": True
    },

    # Bank of Japan — official press releases, free.
    {
        "name": "Bank of Japan",
        "type": "rss",
        "url": "https://www.boj.or.jp/en/rss/whatsnew.xml",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "free",
        "region": "Asia",
        "enabled": True
    },

    # Reserve Bank of India — official press releases, free.
    {
        "name": "Reserve Bank of India",
        "type": "rss",
        "url": "https://www.rbi.org.in/pressreleases_rss.xml",
        "max_articles": 20,
        "text_mode": "full",
        "access_type": "free",
        "region": "Asia",
        "enabled": True
    }

]
