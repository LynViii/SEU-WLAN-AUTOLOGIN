// HarmonyOS ArkTS proof of concept.
// This is the reusable authentication core, not a complete HAP application.

import { http } from '@kit.NetworkKit';

const STATUS_URL: string = 'https://w.seu.edu.cn/drcom/chkstatus?callback=dr1002';
const LOGIN_URL: string = 'https://w.seu.edu.cn:801/eportal/';

export interface SeuStatus {
  authenticated: boolean;
  ip: string;
}

function parseJsonp(payload: string): Record<string, Object> {
  const start: number = payload.indexOf('{');
  const end: number = payload.lastIndexOf('}');
  if (start < 0 || end <= start) {
    throw new Error('Invalid JSONP response');
  }
  return JSON.parse(payload.substring(start, end + 1)) as Record<string, Object>;
}

async function getText(url: string): Promise<string> {
  const request = http.createHttp();
  try {
    const response = await request.request(url, {
      method: http.RequestMethod.GET,
      connectTimeout: 5000,
      readTimeout: 8000
    });
    return String(response.result);
  } finally {
    request.destroy();
  }
}

export async function getStatus(): Promise<SeuStatus> {
  const data = parseJsonp(await getText(STATUS_URL));
  const result = String(data['result'] ?? '');
  const ip = String(data['v46ip'] ?? data['v4ip'] ?? data['ss5'] ?? '');

  if (result !== '0' && result !== '1') {
    throw new Error('Unknown gateway status: ' + result);
  }
  return { authenticated: result === '1', ip };
}

export async function login(username: string, password: string): Promise<SeuStatus> {
  const current = await getStatus();
  if (current.authenticated) {
    return current;
  }
  if (!current.ip) {
    throw new Error('Missing campus network IP');
  }

  const query: string =
    'c=Portal' +
    '&a=login' +
    '&callback=dr1003' +
    '&login_method=1' +
    '&user_account=' + encodeURIComponent(',0,' + username.trim()) +
    '&user_password=' + encodeURIComponent(password) +
    '&wlan_user_ip=' + encodeURIComponent(current.ip);

  const result = parseJsonp(await getText(LOGIN_URL + '?' + query));
  if (String(result['result'] ?? '') !== '1') {
    throw new Error('SEU WLAN authentication rejected');
  }

  const verified = await getStatus();
  if (!verified.authenticated) {
    throw new Error('Login returned success but verification failed');
  }
  return verified;
}
