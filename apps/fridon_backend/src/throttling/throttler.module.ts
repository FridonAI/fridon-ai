import { Module } from '@nestjs/common';
import { ThrottlerModule as NestThrottlerModule } from '@nestjs/throttler';
import { CacheWalletThrottlerStorage } from './cache-wallet-throttler.storage';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from '@nestjs/cache-manager';

@Module({
  imports: [
    NestThrottlerModule.forRootAsync({
      inject: [CACHE_MANAGER],
      useFactory: (cacheManager: Cache) => ({
        storage: new CacheWalletThrottlerStorage(cacheManager),
        throttlers: [
          {
            name: 'chat',
            limit: 45,
            ttl: 86400000,
          },
        ],
      }),
    }),
  ],
  providers: [CacheWalletThrottlerStorage],
  exports: [NestThrottlerModule],
})
export class ThrottlerModule {}
