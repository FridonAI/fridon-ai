import { Auth, Wallet, WalletSession } from '@lib/auth';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Controller, Get, Inject } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { Cache } from 'cache-manager';
import { THROTTLER_LIMIT, THROTTLER_TTL } from './throttler.module';

@Controller('throttling')
@ApiTags('throttling')
@Auth()
export class ThrottlingController {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  @Get('limit')
  async getDailyLimit(@Wallet() wallet: WalletSession) {
    // Generate key and retrieve limit information from the cache.
    const key = `ChatHttpController-createChatMessage-${wallet.walletAddress}`;

    const limitInfo = await this.cacheManager.get<number[]>(
      this.getKey(key, 'chat'),
    );

    return {
      currentLimit: limitInfo?.length || 0,
      remainingLimit: THROTTLER_LIMIT - (limitInfo?.length || 0),
      maxLimit: THROTTLER_LIMIT,
      ttl: THROTTLER_TTL,
    };
  }

  private getKey(key: string, throttlerName: string): string {
    return `throttle:${throttlerName}:${key}`;
  }
}
