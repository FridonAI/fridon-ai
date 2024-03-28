import { Module } from '@nestjs/common';
import { MediasService } from './medias.service';
import { MediaController } from './medias.controller';

@Module({
  controllers: [MediaController],
  providers: [MediasService],
})
export class UserModule {}
