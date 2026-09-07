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


    # ========================================================
    # MARGINAL REVOLUTION
    # Broad economics blog; MacroDrive relevance filtering
    # removes posts that are not macro-relevant.
    # ========================================================

    {
        "name": "Marginal Revolution",
        "type": "rss",
        "url": "https://marginalrevolution.com/feed",
        "max_articles": 20,
        "text_mode": "provided",
        "access_type": "free",
        "enabled": True
    },


]