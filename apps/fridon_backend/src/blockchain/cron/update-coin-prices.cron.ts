import { Inject, Logger, OnModuleInit } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { BlockchainTools } from '../utils/tools/blockchain-tools';

export class UpdateCoinPrices implements OnModuleInit {
  private readonly l = new Logger(UpdateCoinPrices.name);

  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    private tools: BlockchainTools,
  ) {}

  async onModuleInit() {
    this.l.log('Called Update Token Prices onModuleInit');

    const coinPrices = await this.tools.fetchCoinPricesCoinGecko();

    await this.cacheManager.set('coinPrices', coinPrices, 300 * 1000);
  }

  @Cron(CronExpression.EVERY_30_MINUTES)
  async execute() {
    this.l.log('Called Update Token Prices Cron Job');

    const coinPrices = await this.tools.fetchCoinPricesCoinGecko();

    await this.cacheManager.set('coinPrices', coinPrices, 300 * 1000);
  }
}
