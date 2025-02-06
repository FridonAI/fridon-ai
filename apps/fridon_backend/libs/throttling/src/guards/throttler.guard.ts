import { Injectable } from '@nestjs/common';
import { Logger } from '@nestjs/common';
import { ThrottlerGuard } from '@nestjs/throttler';
import { ExecutionContext } from '@nestjs/common';
import { HttpException, HttpStatus } from '@nestjs/common';

@Injectable()
export class WalletThrottlerGuard extends ThrottlerGuard {
  private readonly logger = new Logger(WalletThrottlerGuard.name);

  override async handleRequest(requestProps: {
    context: ExecutionContext;
    limit: number;
    ttl: number;
  }): Promise<boolean> {
    const { context, limit, ttl } = requestProps;
    const request = context.switchToHttp().getRequest();
    const { walletAddress } = request.walletSession;

    if (!walletAddress) {
      this.logger.warn('No wallet address found in request');
      return true;
    }

    const key = `${context.getClass().name}-${context.getHandler().name}-${walletAddress}`;
    const result = await this.storageService.increment(
      key,
      ttl,
      limit,
      ttl,
      'chat',
    );

    if (result.isBlocked) {
      this.logger.warn(`Rate limit exceeded for wallet ${walletAddress}`);
      throw new HttpException(
        'Too Many Requests',
        HttpStatus.TOO_MANY_REQUESTS,
      );
    }

    return true;
  }
}
