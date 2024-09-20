import { Body, Controller, Get, Param, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import {
  FollowMediasBodyRequestDto,
  GetFollowedMediasParamsRequestDto,
  GetMediasResponseDto,
  UnfollowMediasBodyRequestDto,
} from './medias.dto';
import { MediasService } from './medias.service';

@Controller('medias')
@ApiTags('medias')
export class MediaController {
  constructor(private readonly mediasService: MediasService) {}

  @Post('/follow')
  async followMedia(@Body() body: FollowMediasBodyRequestDto): Promise<void> {
    await this.mediasService.followMedia(body.walletId, body.server);
  }

  @Post('/unfollow')
  async unfollowMedia(
    @Body() body: UnfollowMediasBodyRequestDto,
  ): Promise<void> {
    await this.mediasService.unfollowMedia(body.walletId, body.server);
  }

  @Get('/wallet/:walletId')
  async getFollowedMedia(
    @Param() { walletId }: GetFollowedMediasParamsRequestDto,
  ): Promise<GetMediasResponseDto> {
    return {
      medias: await this.mediasService.getFollowedMedia(walletId),
    };
  }

  @Get('/')
  async getMedia(): Promise<GetMediasResponseDto> {
    return {
      medias: await this.mediasService.getMedias(),
    };
  }
}
