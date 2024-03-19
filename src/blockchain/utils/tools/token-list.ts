import { Inject } from '@nestjs/common';
import { SplTokenType, TokenListJsonType, TokenListType } from '../types';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';

const STRICT_TOKEN_LIST_URL = 'https://token.jup.ag/strict';

export class BlockchainTools {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async fetchTokenList(): Promise<TokenListType> {
    const data = await fetch(STRICT_TOKEN_LIST_URL);
    const tokenListJson: TokenListJsonType[] = await data.json();

    const tokenList: TokenListType = tokenListJson.map((token) => {
      return {
        mintAddress: token.address,
        decimals: token.decimals,
        name: token.name,
        symbol: token.symbol,
      } as SplTokenType;
    });

    return tokenList;
  }

  async convertSymbolToMintAddress(symbol: string): Promise<string> {
    const cachedTokenList: TokenListType | undefined =
      await this.cacheManager.get('tokenList');

    const strictTokenList = cachedTokenList || (await this.fetchTokenList());

    const token = strictTokenList.find(
      (token) => token.symbol.toLowerCase() === symbol.toLowerCase(),
    );

    if (!token) {
      throw new Error(`Token with symbol ${symbol} not found`);
    }
    return token.mintAddress;
  }
}
