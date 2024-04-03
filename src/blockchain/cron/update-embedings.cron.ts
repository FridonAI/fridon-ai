import pgvector from 'pgvector';
import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { readFileSync } from 'fs';
import { PrismaService } from 'nestjs-prisma';
import { HuggingFaceAdapter } from '../external/hugging-face.adapter';
import { BirdEyeAdapter } from '../external/bird-eye.adapter';

@Injectable()
export class UpdateEmbeddings {
  private readonly l = new Logger(UpdateEmbeddings.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly huggingFaceAdapter: HuggingFaceAdapter,
    private readonly birdEyeAdapter: BirdEyeAdapter,
  ) {}

  @Cron(CronExpression.EVERY_5_SECONDS)
  async execute() {
    this.l.debug('Called Update Embeddings Cron Job');

    const tokenAddresses = this.getTokenAddresses();

    const arr: number[][] = [];
    for (const token of tokenAddresses) {
      const data = await this.getBirdEyeData(token.address);
      arr.push(data);
    }

    const result = await this.huggingFaceAdapter.getEmbeddings(arr);
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
    const data = await this.birdEyeAdapter.getHistoryPrice(
      tokenAddress,
      timeFrom,
      timeTo,
    );

    while (data.length < 512) {
      data.unshift(0);
    }
    return data;
  }
}
