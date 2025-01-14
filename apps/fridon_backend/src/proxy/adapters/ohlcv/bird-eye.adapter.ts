import { BadRequestException, Injectable, Logger, NotFoundException } from '@nestjs/common';
import { JupiterTokenListAdapter } from '../token-list/token-list.adapter';
import { OHLCVAdapter, type OHLCV } from './ohlcv.adapter';

type BirdEyeResponse =
  | {
    success: true;
    data: {
      items: { unixTime: number; o: number; h: number; l: number; c: number; v: number }[];
    };
  }
  | { success: false; message: 'address is invalid format' };

@Injectable()
export class BirdEyeAdapter implements OHLCVAdapter {
  private readonly l: Logger = new Logger(BirdEyeAdapter.name);

  constructor(private readonly tokenListAdapter: JupiterTokenListAdapter) { }

  async getOHLCV(symbol: string, interval: '30m' | '1h' | '4h' | '1d', startTime: number, endTime: number): Promise<OHLCV[]> {
    const tokenList = await this.tokenListAdapter.getTokenList();
    const token = tokenList.find(token => token.symbol.toLowerCase() === symbol.toLowerCase());
    if (!token) {
      throw new NotFoundException(`Token not found: ${symbol}`);
    }

    const intervalMap = {
      '30m': '30m',
      '1h': '1H',
      '4h': '4H',
      '1d': '1D'
    };

    const params = new URLSearchParams({
      address: token.address,
      time_from: startTime.toString(),
      time_to: endTime.toString(),
      type: intervalMap[interval],
    });
    const url = `https://public-api.birdeye.so/defi/ohlcv?${params.toString()}`;
    const result = (await fetch(url, {
      headers: {
        'X-API-KEY': process.env['BIRDEYE_API_KEY']!,
        'x-chain': 'solana',
      },
    }).then((res) => res.json())) as BirdEyeResponse;

    if ('message' in result) {
      this.l.debug(
        `BirdEye Response[${url}]: ${JSON.stringify(result.message)}`,
      );
      throw new BadRequestException(
        `Failed to fetch Birdeye data: "${result.message}"`,
      );
    }
    this.l.debug(`BirdEye Response[${url}]: ${JSON.stringify(result.data)}`);

    return result.data.items.map((item) => ({
      timestamp: item.unixTime,
      open: item.o,
      high: item.h,
      low: item.l,
      close: item.c,
      volume: item.v
    }));
  }
}
