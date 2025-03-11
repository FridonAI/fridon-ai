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
  private readonly marketDataUrl =
    'https://public-api.birdeye.so/defi/v3/token/market-data';
  private readonly birdeyeApiKey = process.env['BIRDEYE_API_KEY'];

  async getTokenList(tags: string[] = ['verified']): Promise<Token[]> {
    if (!this.tokenList) {
      const initialTokenList = await this.fetchTokenList(tags);
      const sortedTokenList = initialTokenList.sort((a, b) =>
        a.symbol.localeCompare(b.symbol),
      );
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
    const duplicateTokens = Array.from(hasDuplicates).flatMap(
      (symbol) => tokensBySymbol.get(symbol) || [],
    );
    const marketData = await this.batchFetchTokenMarketData(
      duplicateTokens.map((token) => token.address),
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
    batchSize: number = 15,
  ): Promise<[string, number][]> {
    const results: [string, number][] = [];

    for (let i = 0; i < tokenList.length; i += batchSize) {
      const batch = tokenList.slice(i, i + batchSize);
      const batchResults = await Promise.all(
        batch.map((token) => this.fetchTokenMarketData(token)),
      );
      results.push(...batchResults);

      if (i + batchSize < tokenList.length) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }

    return results;
  }

  private async fetchTokenMarketData(
    tokenAddress: string,
  ): Promise<[string, number]> {
    const params = new URLSearchParams({ address: tokenAddress });
    const response = await fetch(`${this.marketDataUrl}?${params}`, {
      headers: {
        accept: 'application/json',
        'x-chain': 'solana',
        'X-API-KEY': this.birdeyeApiKey || '',
      },
    });

    const data = (await response.json()) as MarketData;

    if (!data.success || !data.data) {
      return [tokenAddress, 0];
    }

    const marketcap = data.data.marketcap;
    return [tokenAddress, marketcap ?? 0];
  }
}

export class BinanceTokenListAdapter {
  private readonly logger = new Logger(BinanceTokenListAdapter.name);
  private tokenList: Record<string, Token[]> = {};

  async getTokenList(category: string = 'spot'): Promise<string[]> {
    if (!this.tokenList[category]) {
      let url = 'https://api.binance.com/api/v3/exchangeInfo';
      if (category === 'futures') {
        url = 'https://fapi.binance.com/fapi/v1/exchangeInfo';
      }
      const response = await fetch(url);
      try {
        const data = await response.json();
        const symbols = Array.from(
          new Set(data.symbols.map((item: any) => item.baseAsset)),
        );
        this.logger.log(
          `Found ${symbols.length} ${category} tokens on Binance`,
        );
        this.tokenList[category] = symbols;
        return symbols;
      } catch (error) {
        this.logger.error(`Error fetching data: ${error}`);
        return [];
      }
    }
    return this.tokenList[category];
  }
}

export class BybitTokenListAdapter {
  private readonly logger = new Logger(BybitTokenListAdapter.name);
  private tokenList: Record<string, Token[]> = {};

  async getTokenList(category: string = 'spot'): Promise<string[]> {
    if (!this.tokenList[category]) {
      const url = 'https://api.bybit.com/v5/market/instruments-info';
      const params = new URLSearchParams({ category });
      const response = await fetch(`${url}?${params}`);
      try {
        const data = await response.json();
        const symbols = Array.from(
          new Set(data.result.list.map((item: any) => item.baseCoin)),
        );
        this.logger.log(`Found ${symbols.length} ${category} tokens on Bybit`);
        this.tokenList[category] = symbols;
        return symbols;
      } catch (error) {
        this.logger.error(`Error fetching data: ${error}`);
        return [];
      }
    }
    return this.tokenList[category];
  }
}
