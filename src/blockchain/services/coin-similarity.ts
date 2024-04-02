import { BadRequestException, Injectable } from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';
import pgvector from 'pgvector';

type BirdEyeResponse =
  | {
      success: true;
      data: {
        items: { unixTime: number; value: number }[];
      };
    }
  | { success: false; message: 'address is invalid format' };

@Injectable()
export class CoinSimilarityService {
  constructor(private readonly prisma: PrismaService) {}

  async getCoinSimilarity(symbol: string, from: number, to: number, k: number) {
    const data = await this.getBirdEyeData(symbol, from, to);

    const modelUrl =
      'https://kt60ga6c7qc0otgc.us-east-1.aws.endpoints.huggingface.cloud';

    const response = await fetch(modelUrl, {
      method: 'POST',
      headers: {
        Authorization: 'Bearer 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',
        Accept: 'application/json',
        'Content-type': 'application/json',
      },
      body: JSON.stringify({
        inputs: [data],
      }),
    });

    type ModelResponse =
      | {
          vector: [number[]];
        }
      | { error: string };
    const result = (await response.json()) as ModelResponse;
    if ('error' in result) {
      throw new BadRequestException(`Hugging Face error: ${result.error}`);
    }
    const embedding = result.vector[0];
    const vector = pgvector.toSql(embedding);

    type resultType = {
      symbol: string;
      address: string;
    }[];

    const res = await this.prisma.$queryRaw<resultType>`
        SELECT symbol, address
        FROM price_vectors
        WHERE address != ${symbol}
        ORDER BY 1 - (embedding <=> ${vector}::vector) DESC LIMIT ${k}`;
    return res;
  }

  private async getBirdEyeData(
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
