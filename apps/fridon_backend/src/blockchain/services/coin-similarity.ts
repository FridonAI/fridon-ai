import { BadRequestException, Injectable } from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';
import pgvector from 'pgvector';
import { readFileSync } from 'fs';
import { ReplicateAdapter } from '../external/replicate.adapter';
import { BinanceAdapter } from '../external/binance.adapter';

export type TokenAddress = {
  symbol: string;
  address: string;
  chain: string;
};

@Injectable()
export class CoinSimilarityService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly replicateAdapter: ReplicateAdapter,
    private readonly binanceAdapter: BinanceAdapter,
  ) {}

  async updateAllEmbeddings() {
    const tokens = this.getTokens();

    await this.updateEmbeddingsBatch(tokens);
  }

  async updateEmbeddingsBatch(tokens: string[]) {
    const arr: number[][] = [];
    for (const token of tokens) {
      const data = await this.getPriceData(token);
      arr.push(data);
    }

    const result = await this.replicateAdapter.getEmbeddings(arr);
    const richResult = result.vector.map((vector, index) => ({
      vector,
      symbol: tokens[index],
      address: tokens[index],
      chain: 'binance',
      values: arr[index]!,
    }));

    result.vector.forEach(async (vector, i) => {
      const embedding = pgvector.toSql(vector);
      const values = pgvector.toSql(richResult[i]!.values);
      await this.prisma.$executeRaw`
        INSERT INTO price_vectors (embedding, symbol, address, values, chain, "updatedAt")
        VALUES
        (${embedding}::vector, ${richResult[i]!.symbol}, ${richResult[i]!.address}, ${values}::vector, ${richResult[i]!.chain}, NOW())
        ON CONFLICT (symbol, chain) DO UPDATE
        SET
          embedding = EXCLUDED.embedding,
          symbol = EXCLUDED.symbol,
          address = EXCLUDED.address,
          values = EXCLUDED.values,
          chain = EXCLUDED.chain,
          "updatedAt" = NOW();
        `;
    });
  }

  async getCoinSimilarity(symbol: string, from: number, to: number, k: number) {
    const tokenInfo = this.getTokens().find((token) => token === symbol);

    if (!tokenInfo) {
      throw new BadRequestException(`Token[${symbol}] not found`);
    }

    const data = await this.binanceAdapter.getHistoryPrice(
      tokenInfo,
      '4h',
      from,
      to,
      undefined,
    );
    const result = await this.replicateAdapter.getEmbeddings([data]);

    const embedding = result.vector[0];
    const vector = pgvector.toSql(embedding);

    type ResultType = {
      symbol: string;
      score: number;
      address: string;
      chain: string;
    }[];

    const res = await this.prisma.$queryRaw<ResultType>`
        SELECT symbol, 1 - (embedding <=> ${vector}::vector) as score, address, chain
        FROM price_vectors
        WHERE address != ${tokenInfo}
        ORDER BY score DESC LIMIT ${k}`;

    return [
      {
        symbol: symbol,
        address: tokenInfo,
        chain: 'binance',
        score: 1,
      },
      ...res,
    ] as ResultType;
  }

  public getTokenAddresses(): TokenAddress[] {
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

  public getTokens(): string[] {
    try {
      const res = readFileSync(
        './src/blockchain/cron/coins-list-new.json',
        'utf-8',
      );
      return JSON.parse(res);
    } catch {
      const res = readFileSync(
        './dist/blockchain/cron/coins-list-new.json',
        'utf-8',
      );
      return JSON.parse(res);
    }
  }

  private async getPriceData(token: string): Promise<number[]> {
    const data = await this.binanceAdapter.getHistoryPrice(
      token,
      '4h',
      undefined,
      undefined,
      512,
    );

    while (data.length < 512) {
      data.unshift(0);
    }
    return data;
  }
}
