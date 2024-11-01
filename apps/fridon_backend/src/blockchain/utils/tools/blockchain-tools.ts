import { HttpException, Inject } from '@nestjs/common';
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
import { Connection } from '@solana/web3.js';
import { PublicKey } from '@metaplex-foundation/js';
import { WSOL_MINT_ADDRESS } from '../constants';
import { TokenAmount } from './token-amount';
import { CoinGeckoClient, type CoinMarket } from 'coingecko-api-v3';

export const sleep = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

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

  async getTokenBalanceSpl(
    connection: Connection,
    walletAddress: PublicKey,
    tokenAccount: PublicKey,
  ) {
    if (tokenAccount.equals(WSOL_MINT_ADDRESS)) {
      const accountInfo = await connection.getAccountInfo(
        new PublicKey(walletAddress),
      );

      if (!accountInfo) {
        throw new HttpException('Sol Account not found', 404);
      }

      return new TokenAmount(accountInfo!.lamports, 9, true);
    }

    const balance = await connection.getParsedTokenAccountsByOwner(
      walletAddress,
      { mint: tokenAccount },
      'confirmed',
    );

    if (balance.value.length > 1) {
      throw new HttpException('Multiple token accounts found', 404);
    }

    if (balance.value.length === 0) {
      throw new HttpException('Token account not found', 404);
    }

    const result = balance.value.map((val) => {
      const tokenAmount = val.account.data.parsed.info.tokenAmount;
      return new TokenAmount(tokenAmount.amount, tokenAmount.decimals, true);
    })[0];
    if (!result) throw new HttpException('Token account not found', 404);

    return result;
  }

  async fetchCoinPricesCoinGecko(): Promise<BirdeyePrice[]> {
    try {
      // Define CoinGecko client
      const client = new CoinGeckoClient({
        timeout: 100_000,
        autoRetry: true,
      });
      // Get all the coin ids
      const coinPairs = await this.collectCoinIds(client);

      const perPage = 250;
      const total = Object.keys(coinPairs).length;
      const coinPrices: CoinMarket[] = [];

      for (let i = 0; i < 2; i++) {
        console.log('fetching page', i + 1, 'of', Math.ceil(total / perPage));
        try {
          const coinPricesResponse = await client.coinMarket({
            vs_currency: 'usd',
            per_page: perPage,
            page: i + 1,
            // @ts-ignore
            category: 'solana-ecosystem',
            order: 'volume_desc',
          });

          coinPrices.push(...coinPricesResponse);

          await sleep(1000);
        } catch (error) {
          console.error('error fetching prices', error);
        }
      }

      console.log('fetch complete.', coinPrices.length, 'coins fetched');

      coinPrices.map((coin: any) => {
        if (!coinPairs[coin.id]) {
          console.log('no address for', coin.id, coin.symbol, coin.name);
        } else {
          coin.address = coinPairs[coin.id];
        }
      });

      return coinPrices
        .map((coin: any) => {
          return {
            address: coin.address,
            price: coin.current_price
              ? parseFloat(coin.current_price.toFixed(10))
              : undefined,
          };
        })
        .filter((item: any) => item?.address) as BirdeyePrice[];
    } catch (error) {
      console.error('Error fetching coin prices', error);
      // throw new HttpException('Error fetching coin prices', 500);
      return [];
    }
  }

  private async collectCoinIds(client: CoinGeckoClient) {
    const coins = await client.coinList({ include_platform: true });
    const solanaCoins = coins.filter((coin: any) => coin.platforms?.['solana']);

    const coinPairs: Record<string, string> = {
      solana: '11111111111111111111111111111111',
    };

    solanaCoins.map((coin: any) => {
      if (coin.platforms['solana']) {
        coinPairs[coin.id] = coin.platforms['solana'];
      }
    });

    return coinPairs;
  }

  async fetchCoinPrices(): Promise<BirdeyePrice[]> {
    try {
      const coinIds = await this.getMintAddresses();
      const requestUrl =
        'https://public-api.birdeye.so/defi/multi_price?list_address=';

      const coinPricesChunks = await Promise.all(
        _.chunk(coinIds, 100).map(async (coinIdsChunk) => {
          const response = await fetch(
            requestUrl.concat(coinIdsChunk.join(',')),
            {
              headers: {
                'X-API-KEY': process.env['BIRDEYE_API_KEY']!,
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
    } catch (error) {
      console.error('Error fetching coin prices', error);
      throw new HttpException('Error fetching coin prices', 500);
    }
  }

  async getCoinPrices(): Promise<BirdeyePrice[]> {
    const cachedCoinPrices: BirdeyePrice[] | undefined =
      await this.cacheManager.get('coinPrices');

    if (cachedCoinPrices) {
      return cachedCoinPrices;
    }

    const tokenPrices = await this.fetchCoinPricesCoinGecko();

    await this.cacheManager.set('coinPrices', tokenPrices, 300 * 1000);

    return tokenPrices;
  }

  async getTokenPrice(mintAddress: string): Promise<number> {
    const coinPrices = await this.getCoinPrices();
    const tokenPrice = coinPrices.find((coin) => coin.address === mintAddress);

    if (!tokenPrice) {
      throw new HttpException(
        `Token with mint address ${mintAddress} not found`,
        404,
      );
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
        throw new HttpException(
          `Token with mint address ${mintAddress} not found`,
          404,
        );
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

    await this.cacheManager.set('tokenList', tokenList, 24 * 60 * 60 * 1000);

    return tokenList;
  }

  async getMintAddresses(): Promise<string[]> {
    const tokenList = await this.getTokenList();

    return tokenList.map((token) => token.mintAddress);
  }

  async convertSymbolToMintAddress(symbol: string): Promise<string> {
    // convert symbol if needed
    symbol = this.getCurrencySymbol(symbol);

    const tokenList = await this.getTokenList();

    const token = tokenList.find(
      (token) => token.symbol.toLowerCase() === symbol.toLowerCase(),
    );

    if (!token) {
      throw new HttpException(`Token with symbol ${symbol} not found`, 404);
    }
    return token.mintAddress;
  }

  async convertMintAddressToSymbol(mintAddress: string): Promise<string> {
    const tokenList = await this.getTokenList();

    const token = tokenList.find((token) => token.mintAddress === mintAddress);

    if (!token) {
      throw new HttpException(
        `Token with mint address ${mintAddress} not found`,
        404,
      );
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
        throw new HttpException(
          `Token with mint address ${mintAddress} not found`,
          404,
        );
      }
      return token.symbol;
    });
  }

  async findTokenByMintAddress(mintAddress: string): Promise<SplTokenType> {
    const tokenList = await this.getTokenList();

    const token = tokenList.find((token) => token.mintAddress === mintAddress);

    if (!token) {
      throw new HttpException(
        `Token with mint address ${mintAddress} not found`,
        404,
      );
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
        throw new HttpException(
          `Token with mint address ${mintAddress} not found`,
          404,
        );
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
    type: string | undefined = undefined,
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
        type,
      };
    });
  }

  getCurrencySymbol(currency: string): string {
    // Convert the currency to lowercase for comparison
    const currencyLower = currency.toLowerCase();

    // Find the matching enum key based on the currency
    const foundKey = Object.keys(SymbolMapper).find(
      (key) => key.toLowerCase() === currencyLower,
    );

    // If a matching key is found, return its value, else return the currency
    return foundKey
      ? SymbolMapper[foundKey as keyof typeof SymbolMapper]
      : currencyLower;
  }
}

export enum SymbolMapper {
  solana = 'sol',
  jupiter = 'jup',
  wif = '$WIF',
  myro = '$MYRO',
  milk = '$MILK',
  rkt = '$RKT',
  cwif = '$CWIF',
  ben = '$BEN',
  sshib = '$SSHIB',
  marvin = '$MARVIN',
  turbo = '$TURBO',
  gary = '$GARY',
  wnz = '$WNZ',
  yeti = '$YETI',
  swts = '$SWTS',
  bear = '$BEAR',
  pelf = '$PELF',
  ksh = '$KSH',
  tips = '$TIPS',
  ggem = '$GGEM',
  popo = '$POPO',
  snoopy = '$SNOOPY',
  clown = '$Clown',
  force = '$FORCE',
  points = '$POINTS',
  retire = '$RETIRE',
  daumen = '$daumen',
  honey = '$HONEY',
  neon = '$NEON',
  crypt = '$CRYPT',
  fly = '$FLY',
  bozo = '$BOZO',
  frog = '$FROG',
  test = '$TEST',
}
