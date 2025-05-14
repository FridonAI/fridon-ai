import { Global, Module } from '@nestjs/common';
import { PrivyClient } from '@privy-io/server-auth';
import { PrivyService } from './privy.service';

@Global()
@Module({
  controllers: [],
  providers: [
    {
      provide: 'PRIVY_CLIENT',
      useFactory: () => {
        return new PrivyClient(
          process.env['PRIVY_APP_ID'] ?? '',
          process.env['PRIVY_APP_SECRET'] ?? '',
        );
      },
    },
    PrivyService,
  ],
  exports: [PrivyService],
})
export class PrivyModule {}
