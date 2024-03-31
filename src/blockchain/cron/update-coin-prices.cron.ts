import { Inject, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { BlockchainTools } from '../utils/tools/blockchain-tools';

export class UpdateCoinPrices {
  private readonly l = new Logger(UpdateCoinPrices.name);

  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    private tools: BlockchainTools,
  ) {}

  @Cron(CronExpression.EVERY_HOUR)
  async execute() {
    this.l.log('Called Update Token Prices Cron Job');

    const coinPrices = await this.tools.fetchCoinPrices();

    await this.cacheManager.set('coinPrices', coinPrices);
  }
}
