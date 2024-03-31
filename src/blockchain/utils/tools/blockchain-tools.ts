import { Inject } from '@nestjs/common';
import {
  BalanceType,
  SplTokenType,
  TokenListJsonType,
  TokenListType,
} from '../types';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { Position } from '@hubbleprotocol/kamino-lending-sdk';
import { NumberFormatter } from './number-formatter';
import { TokenBalance } from '../../providers/wallet-factory';
import _ from 'lodash';

const STRICT_TOKEN_LIST_URL = 'https://token.jup.ag/strict';
type BirdeyeTokensPrice = {
  [key: string]: {
    value: number;
    updateUnixTime: number;
    updateHumanTime: string;
    priceChange24h: number;
  };
};

type BirdeyeTokensPriceJson = {
  data: BirdeyeTokensPrice[];
  success: boolean;
};

export type BirdeyePrice = {
  address: string;
  price: number;
};

export class BlockchainTools {
  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    private numberFormatter: NumberFormatter,
  ) {}

  async fetchCoinPrices() {
    const coinIds = await this.getMintAddresses();
    const requestUrl =
      'https://public-api.birdeye.so/public/multi_price?list_address=';

    const coinPricesChunks = await Promise.all(
      _.chunk(coinIds, 100).map(async (coinIdsChunk) => {
        const response = await fetch(
          requestUrl.concat(coinIdsChunk.join(',')),
          {
            headers: {
              'X-API-KEY': '1ce5e10d345740ecb60ef4bb960d0385',
            },
          },
        );
        const parsedJson: BirdeyeTokensPriceJson = await response.json();
        return parsedJson.data;
      }),
    );

    const coinPrices = coinPricesChunks.flat();

    const prices = coinPrices
      .flatMap((coins) => {
        return Object.entries(coins)
          .map(([key, value]) => {
            if (!value) return undefined;
            return {
              address: key,
              price: value.value
                ? parseFloat(value.value.toFixed(10))
                : undefined,
            };
          })
          .filter((item: any) => item) as BirdeyePrice[];
      })
      .flat();

    return prices;
  }

  async getCoinPrices(): Promise<BirdeyePrice[]> {
    const cachedCoinPrices: BirdeyePrice[] | undefined =
      await this.cacheManager.get('coinPrices');

    if (cachedCoinPrices) {
      return cachedCoinPrices;
    }

    const tokenPrices = await this.fetchCoinPrices();

    await this.cacheManager.set('coinPrices', tokenPrices);

    return tokenPrices;
  }

  async getTokenPrice(mintAddress: string): Promise<number> {
    const coinPrices = await this.getCoinPrices();
    const tokenPrice = coinPrices.find((coin) => coin.address === mintAddress);

    if (!tokenPrice) {
      throw new Error(`Token with mint address ${mintAddress} not found`);
    }

    return tokenPrice.price;
  }

  async getTokenPrices(mintAddresses: string[]): Promise<BirdeyePrice[]> {
    const coinPrices = await this.getCoinPrices();
    const tokenPrices = mintAddresses.map((mintAddress) => {
      const tokenPrice = coinPrices.find(
        (coin) => coin.address === mintAddress,
      );

      if (!tokenPrice) {
        throw new Error(`Token with mint address ${mintAddress} not found`);
      }

      return tokenPrice;
    });

    return tokenPrices;
  }

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

  async getTokenList(): Promise<TokenListType> {
    const cachedTokenList: TokenListType | undefined =
      await this.cacheManager.get('tokenList');

    if (cachedTokenList) {
      return cachedTokenList;
    }

    const tokenList = await this.fetchTokenList();

    await this.cacheManager.set('tokenList', tokenList);

    return tokenList;
  }

  async getMintAddresses(): Promise<string[]> {
    const tokenList = await this.getTokenList();

    return tokenList.map((token) => token.mintAddress);
  }

  async convertSymbolToMintAddress(symbol: string): Promise<string> {
    const tokenList = await this.getTokenList();

    const token = tokenList.find(
      (token) => token.symbol.toLowerCase() === symbol.toLowerCase(),
    );

    if (!token) {
      throw new Error(`Token with symbol ${symbol} not found`);
    }
    return token.mintAddress;
  }

  async convertMintAddressToSymbol(mintAddress: string): Promise<string> {
    const tokenList = await this.getTokenList();

    const token = tokenList.find((token) => token.mintAddress === mintAddress);

    if (!token) {
      throw new Error(`Token with mint address ${mintAddress} not found`);
    }
    return token.symbol;
  }

  async convertMintAddressesToSymbols(
    mintAddresses: string[],
  ): Promise<string[]> {
    const tokenList = await this.getTokenList();

    return mintAddresses.map((mintAddress) => {
      const token = tokenList.find(
        (token) => token.mintAddress === mintAddress,
      );

      if (!token) {
        throw new Error(`Token with mint address ${mintAddress} not found`);
      }
      return token.symbol;
    });
  }

  async findTokenByMintAddress(mintAddress: string): Promise<SplTokenType> {
    const tokenList = await this.getTokenList();

    const token = tokenList.find((token) => token.mintAddress === mintAddress);

    if (!token) {
      throw new Error(`Token with mint address ${mintAddress} not found`);
    }
    return token;
  }

  async findTokensByMintAddresses(
    mintAddresses: string[],
  ): Promise<SplTokenType[]> {
    const tokenList = await this.getTokenList();

    return mintAddresses.map((mintAddress) => {
      const token = tokenList.find(
        (token) => token.mintAddress === mintAddress,
      );

      if (!token) {
        throw new Error(`Token with mint address ${mintAddress} not found`);
      }
      return token;
    });
  }

  async convertPositionToBalance(position: Position): Promise<BalanceType> {
    const mintAddress = position.mintAddress.toBase58();
    const token = await this.findTokenByMintAddress(mintAddress);
    const price = await this.getTokenPrice(mintAddress);
    const amount = this.numberFormatter.toUINumber(
      position.amount,
      token.decimals,
    );
    return {
      symbol: token.symbol,
      mintAddress,
      amount,
      value: (price * parseFloat(amount)).toFixed(10),
    };
  }

  async convertTokenBalanceToBalance(
    token: TokenBalance,
  ): Promise<BalanceType> {
    const symbol = await this.convertMintAddressToSymbol(token.mint);
    const price = await this.getTokenPrice(token.mint);
    return {
      symbol: symbol,
      mintAddress: token.mint,
      amount: token.amount,
      value: (price * parseFloat(token.amount)).toFixed(10),
    };
  }

  async convertTokenBalancesToBalances(
    tokens: TokenBalance[],
  ): Promise<BalanceType[]> {
    const mintAddresses = tokens.map((token) => token.mint);
    const symbols = await this.convertMintAddressesToSymbols(mintAddresses);
    const prices = await this.getTokenPrices(mintAddresses);

    return tokens.map((token, index) => {
      const price = prices[index]?.price ?? 0;
      return {
        symbol: symbols[index] ?? 'Unknown',
        mintAddress: token.mint,
        amount: token.amount,
        value: (price * parseFloat(token.amount)).toFixed(10),
      };
    });
  }

  async convertPositionsToBalances(
    positions: Position[],
  ): Promise<BalanceType[]> {
    const mintAddresses = positions.map((position) =>
      position.mintAddress.toBase58(),
    );
    const tokens = await this.findTokensByMintAddresses(mintAddresses);
    const prices = await this.getTokenPrices(mintAddresses);

    return positions.map((position, index) => {
      const token = tokens[index];
      const price = prices[index]?.price ?? 0;
      const decimals = token?.decimals ?? 0;
      return {
        symbol: token?.symbol ?? 'Unknown',
        mintAddress: position.mintAddress.toBase58(),
        amount: this.numberFormatter.toUINumber(position.amount, decimals),
        value: (
          price *
          parseFloat(this.numberFormatter.toUINumber(position.amount, decimals))
        ).toFixed(10),
      };
    });
  }
}
