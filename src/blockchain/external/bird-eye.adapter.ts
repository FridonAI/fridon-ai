import { BadRequestException } from '@nestjs/common';

type BirdEyeResponse =
  | {
      success: true;
      data: {
        items: { unixTime: number; value: number }[];
      };
    }
  | { success: false; message: 'address is invalid format' };

export class BirdEyeAdapter {
  async getHistoryPrice(
    tokenAddress: string,
    from: number,
    to: number,
  ): Promise<number[]> {
    const result = (await fetch(
      `https://public-api.birdeye.so/defi/history_price?address=${tokenAddress}&time_from=${from}&time_to=${to}&type=1H`,
      {
        headers: {
          'X-API-KEY': '1ce5e10d345740ecb60ef4bb960d0385',
        },
      },
    ).then((res) => res.json())) as BirdEyeResponse;

    if ('message' in result) {
      throw new BadRequestException(result.message);
    }

    if (!result.success) {
      throw new BadRequestException('Failed to fetch Birdeye data');
    }

    const data = result.data.items.map((item) => item.value).slice(0, 512);

    return data;
  }
}
