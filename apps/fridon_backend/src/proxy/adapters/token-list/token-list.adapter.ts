import { BadRequestException, Injectable, Logger } from '@nestjs/common';

interface Token {
  symbol: string;
  address: string;
  chain: string;
}

interface MarketData {
  success: boolean;
  data?: {
    marketcap?: number;
  };
}

@Injectable()
export class JupiterTokenListAdapter {
  private readonly logger = new Logger(JupiterTokenListAdapter.name);
  private tokenList: Token[] | null = null;
  private readonly tokensUrl = 'https://tokens.jup.ag/tokens';
  private readonly marketDataUrl = 'https://public-api.birdeye.so/defi/v3/token/market-data';
  private readonly birdeyeApiKey = process.env['BIRDEYE_API_KEY'];

  async getTokenList(tags: string[] = ['verified']): Promise<Token[]> {
    if (!this.tokenList) {
      const initialTokenList = await this.fetchTokenList(tags);
      const sortedTokenList = initialTokenList.sort((a, b) => a.symbol.localeCompare(b.symbol));
      this.tokenList = await this.removeDuplicates(sortedTokenList);
    }
    return this.tokenList;
  }

  resetTokenList(): void {
    this.tokenList = null;
  }

  private async fetchTokenList(tags: string[]): Promise<Token[]> {
    try {
      const params = new URLSearchParams({ tags: tags.join(',') });
      const response = await fetch(`${this.tokensUrl}?${params}`);
      return await response.json();
    } catch (e) {
      this.logger.error(`Failed to fetch token list: ${e}`);
      return [];
    }
  }

  private async removeDuplicates(sortedTokens: Token[]): Promise<Token[]> {
    // Group tokens by symbol
    const tokensBySymbol = new Map<string, Token[]>();
    const hasDuplicates = new Set<string>();

    for (const token of sortedTokens) {
      const existing = tokensBySymbol.get(token.symbol) || [];
      tokensBySymbol.set(token.symbol, [...existing, token]);
      if (existing.length > 0) {
        hasDuplicates.add(token.symbol);
      }
    }

    // Get market data for duplicates
    const duplicateTokens = Array.from(hasDuplicates)
      .flatMap(symbol => tokensBySymbol.get(symbol) || []);
    const marketData = await this.batchFetchTokenMarketData(
      duplicateTokens.map(token => token.address)
    );

    // Create address to marketcap mapping
    const addressToMarketcap = new Map(marketData);

    // Build final token list
    const finalTokenList: Token[] = [];

    for (const [symbol, tokens] of tokensBySymbol.entries()) {
      if (hasDuplicates.has(symbol)) {
        // Keep token with highest marketcap
        const highestMarketcapToken = tokens.reduce((prev, curr) => {
          const prevMarketcap = addressToMarketcap.get(prev.address) || 0;
          const currMarketcap = addressToMarketcap.get(curr.address) || 0;
          return prevMarketcap > currMarketcap ? prev : curr;
        });
        finalTokenList.push(highestMarketcapToken);
      } else {
        finalTokenList.push(tokens[0] as Token);
      }
    }

    return finalTokenList;
  }

  private async batchFetchTokenMarketData(
    tokenList: string[],
    batchSize: number = 15
  ): Promise<[string, number][]> {
    const results: [string, number][] = [];

    for (let i = 0; i < tokenList.length; i += batchSize) {
      const batch = tokenList.slice(i, i + batchSize);
      const batchResults = await Promise.all(
        batch.map(token => this.fetchTokenMarketData(token))
      );
      results.push(...batchResults);

      if (i + batchSize < tokenList.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    return results;
  }

  private async fetchTokenMarketData(tokenAddress: string): Promise<[string, number]> {
    const params = new URLSearchParams({ address: tokenAddress });
    const response = await fetch(`${this.marketDataUrl}?${params}`, {
      headers: {
        'accept': 'application/json',
        'x-chain': 'solana',
        'X-API-KEY': this.birdeyeApiKey || '',
      }
    });

    const data = await response.json() as MarketData;

    if (!data.success || !data.data) {
      return [tokenAddress, 0];
    }

    const marketcap = data.data.marketcap;
    return [tokenAddress, marketcap ?? 0];
  }
}

export class BinanceTokenListAdapter {
    private readonly logger = new Logger(BinanceTokenListAdapter.name);

    getTokenList(): string[] {
        return [
            "BTC",
            "ETH",
            "NEIRO",
            "SOL",
            "SUI",
            "PEPE",
            "OG",
            "WIF",
            "FTT",
            "BNB",
            "XRP",
            "SEI",
            "DOGE",
            "TAO",
            "FET",
            "SANTOS",
            "WLD",
            "SHIB",
            "APT",
            "FTM",
            "EIGEN",
            "PEOPLE",
            "SAGA",
            "RUNE",
            "NEAR",
            "1000SATS",
            "BONK",
            "FLOKI",
            "NOT",
            "DOGS",
            "1MBABYDOGE",
            "CFX",
            "TURBO",
            "AVAX",
            "BOME",
            "WING",
            "LAZIO",
            "CVC",
            "ENA",
            "TRX",
            "ORDI",
            "ARB",
            "HMSTR",
            "LINK",
            "EUR",
            "CATI",
            "BNX",
            "RENDER",
            "TON",
            "TIA",
            "ADA",
            "AAVE",
            "ALPINE",
            "INJ",
            "ZRO",
            "ZK",
            "USTC",
            "MKR",
            "LTC",
            "PORTO",
            "DIA",
            "ARKM",
            "MATIC",
            "PENDLE",
            "ICP",
            "ALT",
            "IO",
            "FIL",
            "GALA",
            "OP",
            "JUP",
            "BCH",
            "STX",
            "ASR",
            "UNI",
            "CELO",
            "BANANA",
            "W",
            "POL",
            "TROY",
            "LUNC",
            "ATM",
            "MANTA",
            "DYDX",
            "CRV",
            "STRK",
            "DOT",
            "FORTH",
            "LUNA",
            "ACH",
            "CHZ",
            "ATOM",
            "YGG",
            "PHB",
            "AR",
            "JTO",
            "LDO",
            "HBAR",
            "SUPER",
            "FIDA",
            "MEME",
            "CKB",
            "OMNI",
            "PYTH",
            "PSG",
            "DEGO",
            "OM",
            "BEAMX",
            "BB",
            "EURI",
            "JASMY",
            "RAY",
            "SUN",
            "PIXEL",
            "BLUR",
            "ROSE",
            "GRT",
            "TRB",
            "VGX",
            "WOO",
            "IMX",
            "SSV",
            "AI",
            "BAR",
            "GAS",
            "KAVA",
            "DYM",
            "JUV",
            "ETC",
            "CITY",
            "XAI",
            "ASTR",
            "CVP",
            "VIDT",
            "ACM",
            "MASK",
            "ENS",
            "RSR",
            "ARK",
            "APE",
            "AUDIO",
            "PORTAL",
            "REI",
            "CAKE",
            "REZ",
            "MINA",
            "VET",
            "ORN",
            "ALGO",
            "VANRY",
            "AST",
            "HIGH",
            "GMT",
            "AEVO",
            "LEVER",
            "FIO",
            "EOS",
            "AXS",
            "SNT",
            "AXL",
            "UNFI",
            "COS",
            "REEF",
            "XLM",
            "TRU",
            "AMP",
            "TNSR",
            "EPX",
            "COTI",
            "THETA",
            "VIC",
            "RAD",
            "CYBER",
            "RARE",
            "EDU",
            "EGLD",
            "UMA",
            "LISTA",
            "LPT",
            "FOR",
            "ACE",
            "NEO",
            "BAKE",
            "SYN",
            "FRONT",
            "SNX",
            "KDA",
            "TWT",
            "DODO",
            "ONG",
            "CTXC",
            "FLOW",
            "RDNT",
            "VIB",
            "SLF",
            "PYR"
        ];
    }
}
