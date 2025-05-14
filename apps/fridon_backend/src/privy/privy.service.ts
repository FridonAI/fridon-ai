import { Inject, Injectable, Logger } from '@nestjs/common';
import { PrivyClient } from '@privy-io/server-auth';

@Injectable()
export class PrivyService {
  private readonly logger = new Logger(PrivyService.name);

  constructor(
    @Inject('PRIVY_CLIENT') private readonly privyClient: PrivyClient,
  ) {}

  async validateToken(token: string) {
    this.logger.log(`Validating token: ${token}`);
    return this.privyClient.verifyAuthToken(token);
  }

  async getUserById(userId: string) {
    this.logger.log(`Getting user by ID: ${userId}`);
    return this.privyClient.getUser({
      idToken: userId,
    });
  }
}
