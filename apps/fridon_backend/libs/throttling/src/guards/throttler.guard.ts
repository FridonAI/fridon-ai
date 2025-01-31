import {
  BadRequestException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { Logger } from '@nestjs/common';
import { ThrottlerGuard, ThrottlerStorage } from '@nestjs/throttler';
import { ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { HttpException, HttpStatus } from '@nestjs/common';
import { ClaimsType } from 'src/auth/decorators/claims.decorator';

@Injectable()
export class WalletThrottlerGuard extends ThrottlerGuard {
  private readonly logger = new Logger(WalletThrottlerGuard.name);

  constructor(
    options: { throttlers: any[] },
    storageService: ThrottlerStorage,
    reflector: Reflector,
  ) {
    super(options, storageService, reflector);
  }

  override async handleRequest(requestProps: {
    context: ExecutionContext;
    limit: number;
    ttl: number;
  }): Promise<boolean> {
    const { context, limit, ttl } = requestProps;
    const request = context.switchToHttp().getRequest();

    const claims = this.getClaims(request);
    const walletAddress = claims.sub;

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
    console.log('ttl', ttl);
    console.log('limit', limit);

    if (result.isBlocked) {
      this.logger.warn(`Rate limit exceeded for wallet ${walletAddress}`);
      throw new HttpException(
        'Too Many Requests',
        HttpStatus.TOO_MANY_REQUESTS,
      );
    }

    return true;
  }

  private getClaims(request: Request): ClaimsType {
    // @ts-expect-error: This is not a valid type
    const authToken = request.headers['authorization'];
    if (!authToken)
      throw new UnauthorizedException('No authorization token found');

    return this.parseAuthTokenToClaims(authToken);
  }

  private parseAuthTokenToClaims(authToken: string): ClaimsType {
    const claimsStr = Buffer.from(authToken, 'base64').toString();
    try {
      return JSON.parse(claimsStr);
    } catch (error: any) {
      console.log('error', error);
      throw new BadRequestException('Failed to parse token');
    }
  }
}
