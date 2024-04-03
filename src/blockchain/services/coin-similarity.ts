import {
  BadRequestException,
  Injectable,
  Logger,
  OnApplicationBootstrap,
} from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';
import pgvector from 'pgvector';
import { HuggingFaceAdapter } from '../external/hugging-face.adapter';
import { BirdEyeAdapter } from '../external/bird-eye.adapter';
import { readFileSync } from 'fs';

@Injectable()
export class CoinSimilarityService implements OnApplicationBootstrap {
  private readonly l = new Logger(CoinSimilarityService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly huggingFaceAdapter: HuggingFaceAdapter,
    private readonly birdEyeAdapter: BirdEyeAdapter,
  ) {}

  onApplicationBootstrap() {
    this.l.debug('Application Bootstrap: Updating Embeddings');
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    this.updateEmbeddings().then(() => {
      this.l.debug('Application Bootstrap: Embeddings Updated');
    });
  }

  async updateEmbeddings() {
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

  async getCoinSimilarity(symbol: string, from: number, to: number, k: number) {
    const symbolAddress = this.getTokenAddresses().find(
      (token) => token.symbol === symbol,
    )?.address;

    if (!symbolAddress) {
      throw new BadRequestException(`Token[${symbol}] not found`);
    }
    console.log(symbolAddress);

    const data = await this.birdEyeAdapter.getHistoryPrice(symbol, from, to);
    const result = await this.huggingFaceAdapter.getEmbeddings([data]);

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

  private getTokenAddresses(): {
    symbol: string;
    address: string;
  }[] {
    try {
      const res = readFileSync(
        './src/blockchain/cron/coins-list.json',
        'utf-8',
      );
      return JSON.parse(res);
    } catch {
      const res = readFileSync(
        './dist/blockchain/cron/coins-list.json',
        'utf-8',
      );
      return JSON.parse(res);
    }
  }

  private async getBirdEyeData(tokenAddress: string): Promise<number[]> {
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
