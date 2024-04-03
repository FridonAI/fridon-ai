import { Injectable } from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';
import pgvector from 'pgvector';
import { HuggingFaceAdapter } from '../external/hugging-face.adapter';
import { BirdEyeAdapter } from '../external/bird-eye.adapter';

@Injectable()
export class CoinSimilarityService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly huggingFaceAdapter: HuggingFaceAdapter,
    private readonly birdEyeAdapter: BirdEyeAdapter,
  ) {}

  async getCoinSimilarity(symbol: string, from: number, to: number, k: number) {
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
}
