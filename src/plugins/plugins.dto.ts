import { Plugin } from './plugins.repository';

export type FindAllPluginsDtoResponseDto = Plugin & {
  subscribersCount: number;
};
