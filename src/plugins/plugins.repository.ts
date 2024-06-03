import { Injectable } from '@nestjs/common';

export type Plugin = any;

@Injectable()
export class PluginsRepository {
  private plugins: Plugin[] = [];

  set(plugins: Plugin[]) {
    this.plugins = [...plugins];
  }

  findAll(): Plugin[] {
    return this.plugins;
  }
}
