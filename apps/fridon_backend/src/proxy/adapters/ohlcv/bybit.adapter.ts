import { BadRequestException, Injectable, Logger } from '@nestjs/common';
import { OHLCVAdapter, type OHLCV } from './ohlcv.adapter';

type BybitResponse =
  | {
      retCode: 0;
      result: {
        list: [
          string, // Start time
          string, // Open price
          string, // High price
          string, // Low price
          string, // Close price
          string, // Volume
          string, // Turnover
        ][];
      };
    }
  | { retCode: number; retMsg: string };

@Injectable()
export class BybitAdapter implements OHLCVAdapter {
  private readonly logger = new Logger(BybitAdapter.name);

  async getOHLCV(
    symbol: string,
    interval: '30m' | '1h' | '4h' | '1d',
    startTime: number,
    endTime: number,
    category: string = 'spot',
  ): Promise<OHLCV[]> {
    const intervalMap = {
      '30m': '30',
      '1h': '60',
      '4h': '240',
      '1d': 'D',
    };

    const params = new URLSearchParams({
      symbol: `${symbol.toUpperCase()}USDT`,
      interval: intervalMap[interval],
      start: (startTime * 1000).toString(),
      end: (endTime * 1000).toString(),
      category,
      limit: '1000',
    });

    const url = `https://api.bybit.com/v5/market/kline?${params.toString()}`;

    this.logger.log(`Fetching Bybit OHLCV data: ${url}`);

    const response = await fetch(url);
    const result = (await response.json()) as BybitResponse;

    if (result.retCode !== 0) {
      throw new BadRequestException(
        `Failed to fetch Bybit data for ${symbol}: "${result.retMsg}"`,
      );
    }

    if (!result.result.list || result.result.list.length === 0) {
      throw new BadRequestException(
        `No data returned from Bybit for ${symbol}`,
      );
    }

    return result.result.list.reverse().map((item) => ({
      timestamp: Math.floor(Number(item[0]) / 1000),
      open: Number(item[1]),
      high: Number(item[2]),
      low: Number(item[3]),
      close: Number(item[4]),
      volume: Number(item[5]),
    }));
  }
}
