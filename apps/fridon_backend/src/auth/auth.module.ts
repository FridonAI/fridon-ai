import { Module } from '@nestjs/common';
import { AuthController } from './auth.controller';
import { PrivyModule } from 'src/privy/privy.module';
import { AuthService } from './auth.service';

@Module({
  imports: [PrivyModule],
  controllers: [AuthController],
  providers: [AuthService],
})
export class AuthModule {}
