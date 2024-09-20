import { BadRequestException, Logger } from '@nestjs/common';

type BirdEyeResponse =
  | {
      success: true;
      data: {
        items: { unixTime: number; value: number }[];
      };
    }
  | { success: false; message: 'address is invalid format' };

export class BirdEyeAdapter {
  private readonly l: Logger = new Logger(BirdEyeAdapter.name);

  async getHistoryPrice(
    tokenAddress: string,
    chain: string,
    from: number,
    to: number,
  ): Promise<number[]> {
    const url = `https://public-api.birdeye.so/defi/history_price?address=${tokenAddress}&time_from=${from}&time_to=${to}&type=1H`;
    const result = (await fetch(url, {
      headers: {
        'X-API-KEY': process.env['BIRDEYE_API_KEY']!,
        'x-chain': chain,
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

    const data = result.data.items.map((item) => item.value).slice(0, 512);

    return data;
  }
}
