import {
  CanActivate,
  ExecutionContext,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { Request } from 'express';

/**
 * `AuthGuard` validates and attaches an active wallet session to the request.
 *
 * Essential for routes requiring authentication and for `AuthWallet ParamDecorator` functionality.
 */
@Injectable()
export class AuthGuard implements CanActivate {
  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const token = this.extractTokenFromCookie(request);
    if (!token) {
      throw new UnauthorizedException();
    }

    request.walletSession = {
      walletAddress: token,
    };

    return true;
  }

  private extractTokenFromCookie(request: Request): string | undefined {
    return request.cookies['authorization'];
  }
}
