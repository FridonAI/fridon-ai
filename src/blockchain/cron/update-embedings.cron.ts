import pgvector from 'pgvector';
import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { readFileSync } from 'fs';
import { PrismaService } from 'nestjs-prisma';

type BirdEyeResponse = {
  data: {
    items: { unixTime: number; value: number }[];
    success: true;
  };
};

type ModelResponse = {
  vector: number[][];
};

@Injectable()
export class UpdateEmbeddings {
  private readonly l = new Logger(UpdateEmbeddings.name);

  constructor(private readonly prisma: PrismaService) {}

  @Cron(CronExpression.EVERY_5_SECONDS)
  async execute() {
    this.l.debug('Called Update Embeddings Cron Job');

    const tokenAddresses = this.getTokenAddresses();

    const arr: number[][] = [];
    for (const token of tokenAddresses) {
      const data = await this.getBirdEyeData(token.address);
      arr.push(data);
    }

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
        inputs: arr,
      }),
    });

    const result = (await response.json()) as ModelResponse;
    const richResult = result.vector.map((vector, index) => ({
      vector,
      symbol: tokenAddresses[index]!.symbol,
      address: tokenAddresses[index]!.address,
      values: arr[index]!,
    }));

    result.vector.forEach(async (vector, i) => {
      const embedding = pgvector.toSql(vector);
      const values = pgvector.toSql(richResult[i]!.values);
      await this.prisma.$executeRaw`
          INSERT INTO price_vectors 
          (embedding, symbol, address, values) 
          VALUES
          (${embedding}::vector,${richResult[i]!.symbol}, ${richResult[i]!.address}, ${values}::vector)`;
    });
  }

  getTokenAddresses(): {
    symbol: string;
    address: string;
  }[] {
    const res = readFileSync('./src/blockchain/cron/coins-list.json', 'utf-8');
    return JSON.parse(res);
  }

  async getBirdEyeData(tokenAddress: string): Promise<number[]> {
    const timeTo = new Date().getTime();
    const timeFrom = timeTo - 60 * 60 * 24 * 30;
    const result = (await fetch(
      `https://public-api.birdeye.so/defi/history_price?address=${tokenAddress}&time_from=${timeFrom}&time_to=${timeTo}&type=1H`,
      {
        headers: {
          'X-API-KEY': '1ce5e10d345740ecb60ef4bb960d0385',
        },
      },
    ).then((res) => res.json())) as BirdEyeResponse;

    const data = result.data.items.map((item) => item.value).slice(0, 512);

    while (data.length < 512) {
      data.unshift(0);
    }
    return data;
  }
}
