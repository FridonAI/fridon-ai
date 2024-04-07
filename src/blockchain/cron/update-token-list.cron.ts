import { Inject, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { BlockchainTools } from '../utils/tools/blockchain-tools';

export class UpdateTokenList {
  private readonly l = new Logger(UpdateTokenList.name);

  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    private tools: BlockchainTools,
  ) {}

  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  async execute() {
    this.l.log('Called Update Token List Cron Job');

    const tokenList = await this.tools.fetchTokenList();

    await this.cacheManager.set('tokenList', tokenList, 24 * 60 * 60 * 1000);
  }
}
