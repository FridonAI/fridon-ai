import { HttpException, HttpStatus, Logger } from '@nestjs/common';
import { CommandHandler, ICommandHandler } from '@nestjs/cqrs';
import { AuthRepository } from '../../database/auth.repository';
import { SecretsService } from '../../domain-services/secrets.service';
import { sign, verify } from '../../domain/utils';
import { SignInCommand } from './sign-in.command';

/**
 * This service ...
 */

const EXP_SECONDS = 60 * 60 * 24;

@CommandHandler(SignInCommand)
export class SignInService implements ICommandHandler<SignInCommand> {
  private readonly logger = new Logger(SignInService.name);

  constructor(
    // private publisher: EventPublisher,
    private authRepository: AuthRepository,
    private secretsService: SecretsService,
  ) {}

  async execute(command: SignInCommand) {
    this.logger.debug('CreateUserService executed!');

    const { walletAddress, signature } = command;

    console.log(walletAddress, signature);

    // 1. Check Nonce
    const nonce = await this.authRepository.getNonce(walletAddress);
    if (!nonce) {
      throw new HttpException('WalletNotFound', HttpStatus.NOT_FOUND);
    }

    if (!nonce.verifiedAt) {
      throw new HttpException('NonceNotVerified', HttpStatus.UNAUTHORIZED);
    }

    // 2. Verify
    if (
      !(
        verify(nonce.nonce, signature, walletAddress, 'raw') ||
        verify(nonce.nonce, signature, walletAddress, 'transaction') ||
        verify(nonce.nonce, signature, walletAddress, 'versionedTransaction')
      )
    ) {
      throw new HttpException('SignatureInvalid', HttpStatus.FORBIDDEN);
    }

    // 3. Update
    await this.authRepository.updateNonce(walletAddress);
    const serverPublicKey = await this.secretsService.retrieveAuthPublicKey();
    const serverSecretKey = await this.secretsService.retrieveAuthSecretKey();

    // 4. claims
    const iat = Math.floor(Date.now() / 1000);
    const claimsWithoutSig = {
      clientSig: signature,
      nonce: nonce,
      iss: serverPublicKey,
      sub: walletAddress,
      iat: iat,
      exp: iat + EXP_SECONDS,
      userType: nonce.userType,
    };

    // 5. Sign the claims and create the final token
    const serverSignature = sign(
      JSON.stringify(claimsWithoutSig),
      serverSecretKey,
    );
    const claims = {
      ...claimsWithoutSig,
      serverSig: serverSignature,
    };

    // 6. convert claims ot base 64 and return
    const token = Buffer.from(JSON.stringify(claims)).toString('base64');
    return token;
  }
}
