import { HttpException, HttpStatus, Injectable } from '@nestjs/common';
import { PrivyService } from 'src/privy/privy.service';
import { PrismaService } from 'nestjs-prisma';

@Injectable()
export class AuthService {
  constructor(
    private readonly privyService: PrivyService,
    private readonly PrismService: PrismaService,
  ) {}

  async signIn(token: string) {
    try {
      const claims = await this.privyService.validateToken(token);
      const user = await this.privyService.getUserById(claims.userId);

      if (!user) {
        throw new HttpException('User not found', HttpStatus.NOT_FOUND);
      }

      if (!user.wallet?.address) {
        throw new HttpException(
          'Wallet address is required',
          HttpStatus.BAD_REQUEST,
        );
      }

      // Check if user exists in the database
      let userInDb = await this.PrismService.user.findUnique({
        where: {
          privyId: user.id,
        },
      });

      if (!userInDb) {
        // Create a new user in the database
        userInDb = await this.PrismService.user.create({
          data: {
            privyId: user.id,
            email: user.email?.address || null,
            walletId: user.wallet.address,
            twitter: user.twitter?.username || null,
          },
        });
      } else {
        // todo: do we need this? maybe remove it.
        userInDb = await this.PrismService.user.update({
          where: { privyId: user.id },
          data: {
            email: user.email?.address || userInDb.email,
            walletId: user.wallet.address || userInDb.walletId,
            twitter: user.twitter?.username || userInDb.twitter,
          },
        });
      }

      return userInDb;
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      throw new HttpException(
        'Authentication failed:',
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
