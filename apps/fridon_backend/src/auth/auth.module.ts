import { Global, Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { SignInService } from './commands/sign-in/sign-in.service';
import { SignUpController } from './commands/sign-up/sign-up.controller';
import { SignUpService } from './commands/sign-up/sign-up.service';
import { AuthMapper } from './database/auth.mapper';
import { AuthRepository } from './database/auth.repository';
import { SecretsService } from './domain-services/secrets.service';
import { RolesGuard } from './guards/auth.guard';
import { GetNonceController } from './queries/get-nonce/get-nonce.controller';
import { SignInController } from './commands/sign-in/sign-in.controller';

@Global()
@Module({
  imports: [ConfigModule.forRoot()],
  controllers: [SignInController, SignUpController, GetNonceController],
  providers: [
    SignInService,
    SignUpService,
    AuthRepository,
    AuthMapper,
    SecretsService,
    RolesGuard,
  ],
  exports: [SecretsService, RolesGuard],
})
export class AuthModule {}
