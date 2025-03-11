import { BadRequestException, Logger } from '@nestjs/common';
import { OHLCVAdapter, type OHLCV } from './ohlcv.adapter';

type BinanceResponse =
  | [
      [
        number, // Open time
        string, // Open
        string, // High
        string, // Low
        string, // Close (or latest price)
        string, // Volume
        number, // Close time
        string, // Base asset volume
        number, // Number of trades
        string, // Taker buy volume
        string, // Taker buy base asset volume
        string, // Ignore
      ],
    ]
  | { msg: string };

export class BinanceAdapter implements OHLCVAdapter {
  private readonly l: Logger = new Logger(BinanceAdapter.name);

  async getOHLCV(
    symbol: string,
    interval: '30m' | '1h' | '4h' | '1d',
    startTime: number,
    endTime: number,
    category: string = 'spot',
  ): Promise<OHLCV[]> {
    const params = new URLSearchParams({
      symbol: `${symbol.toUpperCase()}USDT`,
      interval,
      startTime: (startTime * 1000).toString(),
      endTime: (endTime * 1000).toString(),
    });

    let baseUrl = 'https://api.binance.com/api/v3/klines';
    if (category === 'futures') {
      baseUrl = 'https://fapi.binance.com/fapi/v1/klines';
    }

    const url = `${baseUrl}?${params.toString()}`;
    this.l.log(`Fetching Binance ${category} OHLCV data: ${url}`);

    const response = await fetch(url);
    const result = (await response.json()) as BinanceResponse;

    if ('msg' in result) {
      throw new BadRequestException(
        `Failed to fetch Binance data for ${symbol}: "${result.msg}"`,
      );
    }
    return result.map((item) => ({
      timestamp: Math.floor(item[0] / 1000),
      open: Number(item[1]),
      high: Number(item[2]),
      low: Number(item[3]),
      close: Number(item[4]),
      volume: Number(item[5]),
    }));
  }
}
