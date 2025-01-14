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

  async getOHLCV(symbol: string, interval: '30m' | '1h' | '4h' | '1d', startTime: number, endTime: number): Promise<OHLCV[]> {
    const params = new URLSearchParams({
      symbol: `${symbol.toUpperCase()}USDT`,
      interval,
      startTime: (startTime * 1000).toString(),
      endTime: (endTime * 1000).toString(),
    });
    const url = `https://api.binance.com/api/v3/klines?${params.toString()}`;
    const response = await fetch(url);
    const result = (await response.json()) as BinanceResponse;

    if ('msg' in result) {
      this.l.debug(`Binance Response[${url}]: ${JSON.stringify(result.msg)}`);
      throw new BadRequestException(
        `Failed to fetch Binance data for ${symbol}: "${result.msg}"`,
      );
    }
    this.l.debug(`Binance Response[${url}]: ${JSON.stringify(result)}`);
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
