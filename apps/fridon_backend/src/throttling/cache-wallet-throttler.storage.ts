import { ThrottlerStorage } from '@nestjs/throttler';
import { ThrottlerStorageRecord } from '@nestjs/throttler/dist/throttler-storage-record.interface';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Inject, Injectable } from '@nestjs/common';
import { Cache } from 'cache-manager';

@Injectable()
export class CacheWalletThrottlerStorage implements ThrottlerStorage {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}

  async increment(
    key: string,
    ttl: number,
    limit: number,
    blockDuration: number,
    throttlerName: string,
  ): Promise<ThrottlerStorageRecord> {
    const record =
      (await this.cacheManager.get<number[]>(
        this.getKey(key, throttlerName),
      )) || [];
    const now = Date.now();
    const newRecord = [...record, now].filter(
      (timestamp) => timestamp > now - ttl,
    );
    await this.cacheManager.set(
      this.getKey(key, throttlerName),
      newRecord,
      ttl,
    );

    const isBlocked = newRecord.length > limit;
    const timeToExpire = ttl - (now - Math.min(...newRecord));

    return {
      totalHits: newRecord.length,
      timeToExpire,
      isBlocked,
      timeToBlockExpire: isBlocked ? blockDuration : 0,
    };
  }

  private getKey(key: string, throttlerName: string): string {
    return `throttle:${throttlerName}:${key}`;
  }
}
