import { BadRequestException, Logger } from '@nestjs/common';

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

export class BinanceAdapter {
  private readonly l: Logger = new Logger(BinanceAdapter.name);

  async getHistoryPrice(
    coin: string,
    interval: string,
    from?: number,
    to?: number,
    limit?: number,
  ): Promise<number[]> {
    let url = `https://api.binance.com/api/v3/klines?symbol=${coin}USDT&interval=${interval}`;
    if (from !== undefined) url += `&startTime=${from}`;
    if (to !== undefined) url += `&endTime=${to}`;
    if (limit !== undefined) url += `&limit=${limit}`;
    const response = await fetch(url);
    const result = (await response.json()) as BinanceResponse;

    if ('msg' in result) {
      this.l.debug(`Binance Response[${url}]: ${JSON.stringify(result.msg)}`);
      throw new BadRequestException(
        `Failed to fetch Binance data for ${coin}: "${result.msg}"`,
      );
    }

    const data = result.map((item) => parseFloat(item[4]));
    return data;
  }
}
