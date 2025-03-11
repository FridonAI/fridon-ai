import { Injectable, Logger } from '@nestjs/common';
import { BinanceAdapter } from './adapters/ohlcv/binance.adapter';
import { BirdEyeAdapter } from './adapters/ohlcv/bird-eye.adapter';
import { BybitAdapter } from './adapters/ohlcv/bybit.adapter';
import { OHLCV } from './adapters/ohlcv/ohlcv.adapter';
import {
  BinanceTokenListAdapter,
  BybitTokenListAdapter,
  JupiterTokenListAdapter,
} from './adapters/token-list/token-list.adapter';

@Injectable()
export class ProxyService {
  private readonly logger = new Logger(ProxyService.name);

  constructor(
    private readonly binanceAdapter: BinanceAdapter,
    private readonly birdeyeAdapter: BirdEyeAdapter,
    private readonly bybitAdapter: BybitAdapter,
    private readonly jupiterTokenListAdapter: JupiterTokenListAdapter,
    private readonly binanceTokenListAdapter: BinanceTokenListAdapter,
    private readonly bybitTokenListAdapter: BybitTokenListAdapter,
  ) {}

  async getOHLCV(
    symbol: string,
    interval: '30m' | '1h' | '4h' | '1d',
    startTime: number,
    endTime: number,
  ): Promise<OHLCV[]> {
    const binanceSpotTokens = await this.binanceTokenListAdapter.getTokenList();

    const isInBinanceSpot = binanceSpotTokens.includes(symbol.toUpperCase());

    if (isInBinanceSpot) {
      try {
        this.logger.log(`Getting OHLCV for ${symbol} from Binance Spot`);
        return await this.binanceAdapter.getOHLCV(
          symbol,
          interval,
          startTime,
          endTime,
          'spot',
        );
      } catch (error: any) {
        this.logger.warn(
          `Failed to get data from Binance Spot: ${error.message}`,
        );
      }
    }
    const bybitSpotTokens = await this.bybitTokenListAdapter.getTokenList();
    const isInBybitSpot = bybitSpotTokens.includes(symbol.toUpperCase());

    if (isInBybitSpot) {
      try {
        this.logger.log(`Getting OHLCV for ${symbol} from Bybit Spot`);
        return await this.bybitAdapter.getOHLCV(
          symbol,
          interval,
          startTime,
          endTime,
          'spot',
        );
      } catch (error: any) {
        this.logger.warn(
          `Failed to get data from Bybit Spot: ${error.message}`,
        );
      }
    }
    const jupTokenList = await this.jupiterTokenListAdapter.getTokenList();
    const isInBirdeye = jupTokenList.some(
      (token) =>
        token.symbol.toLowerCase() === symbol.toLowerCase() ||
        token.symbol.toLowerCase() === `$${symbol.toLowerCase()}`,
    );

    if (isInBirdeye) {
      try {
        this.logger.log(`Getting OHLCV for ${symbol} from Birdeye`);
        return await this.birdeyeAdapter.getOHLCV(
          symbol,
          interval,
          startTime,
          endTime,
        );
      } catch (error: any) {
        this.logger.warn(`Failed to get data from Birdeye: ${error.message}`);
      }
    }

    const binanceFuturesTokens =
      await this.binanceTokenListAdapter.getTokenList('futures');
    const isInBinanceFutures = binanceFuturesTokens.includes(
      symbol.toUpperCase(),
    );

    if (isInBinanceFutures) {
      try {
        this.logger.log(`Getting OHLCV for ${symbol} from Binance Futures`);
        return await this.binanceAdapter.getOHLCV(
          symbol,
          interval,
          startTime,
          endTime,
          'futures',
        );
      } catch (error: any) {
        this.logger.warn(
          `Failed to get data from Binance Futures: ${error.message}`,
        );
      }
    }

    const bybitFuturesTokens =
      await this.bybitTokenListAdapter.getTokenList('futures');
    const isInBybitFutures = bybitFuturesTokens.includes(symbol.toUpperCase());

    if (isInBybitFutures) {
      try {
        this.logger.log(`Getting OHLCV for ${symbol} from Bybit Futures`);
        return await this.bybitAdapter.getOHLCV(
          symbol,
          interval,
          startTime,
          endTime,
          'futures',
        );
      } catch (error: any) {
        this.logger.warn(
          `Failed to get data from Bybit Futures: ${error.message}`,
        );
      }
    }

    throw new Error(
      `Could not fetch OHLCV data for ${symbol} from any provider`,
    );
  }

  async getTokens(keyword: string): Promise<string[]> {
    if (keyword.length > 30) {
      return [keyword];
    }
    const tokenList = await this.jupiterTokenListAdapter.getTokenList();
    const binanceTokenList = await this.binanceTokenListAdapter.getTokenList();
    const bybitTokenList = await this.bybitTokenListAdapter.getTokenList();
    const binanceTokenListFutures =
      await this.binanceTokenListAdapter.getTokenList('futures');
    const bybitTokenListFutures =
      await this.bybitTokenListAdapter.getTokenList('futures');

    return Array.from(
      new Set([
        ...tokenList.map((item) =>
          (item.symbol.startsWith('$')
            ? item.symbol.slice(1)
            : item.symbol
          ).toUpperCase(),
        ),
        ...binanceTokenList,
        ...bybitTokenList,
        ...binanceTokenListFutures,
        ...bybitTokenListFutures,
      ]),
    )
      .filter((token) => token.toUpperCase().startsWith(keyword.toUpperCase()))
      .sort((a, b) => a.localeCompare(b));
  }
}
