import {
  CanActivate,
  ExecutionContext,
  HttpException,
  HttpStatus,
  Injectable,
  Logger,
} from '@nestjs/common';
import { PrivyService } from 'src/privy/privy.service';

@Injectable()
export class PrivyAuthGuard implements CanActivate {
  private readonly logger = new Logger(PrivyAuthGuard.name);
  constructor(private readonly privyService: PrivyService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    this.logger.log('Checking Privy token...');
    const request = context.switchToHttp().getRequest();
    const token = request.headers['authorization']?.split(' ')[1];

    this.logger.log(`Token: ${token}`);
    if (!token) {
      throw new HttpException('No token provided', HttpStatus.UNAUTHORIZED);
    }

    try {
      const claims = await this.privyService.validateToken(token);
      const user = await this.privyService.getUserById(claims.userId);

      request.user = {
        privyId: claims.userId,
        user,
      };
      this.logger.log(`Claims: ${JSON.stringify(request.user)}`);
      return true;
    } catch (error) {
      throw new HttpException('Invalid token', HttpStatus.UNAUTHORIZED);
    }
  }
}
