import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';
import ClientWrapper from './client-wrapper';

export default async function Page() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return (
    <div>
      <App appConfig={appConfig} />
      <ClientWrapper />
    </div>
  );
}
