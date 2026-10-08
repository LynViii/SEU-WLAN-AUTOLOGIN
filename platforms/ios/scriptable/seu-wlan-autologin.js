// SEU WLAN AutoLogin for Scriptable
// Shortcuts default: authenticate.
// Manual run in Scriptable: authenticate / reconfigure / clear credentials.

const STATUS_URL = "https://w.seu.edu.cn/drcom/chkstatus?callback=dr1002";
const LOGIN_URL = "https://w.seu.edu.cn:801/eportal/";
const USERNAME_KEY = "SEU_WLAN_AUTOLOGIN_USERNAME";
const PASSWORD_KEY = "SEU_WLAN_AUTOLOGIN_PASSWORD";

function parseJsonp(text) {
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start < 0 || end <= start) throw new Error("认证网关返回了无法识别的数据");
  return JSON.parse(text.slice(start, end + 1));
}

async function getText(url) {
  const request = new Request(url);
  request.method = "GET";
  request.timeoutInterval = 10;
  return await request.loadString();
}

function hasCredentials() {
  return Keychain.contains(USERNAME_KEY) && Keychain.contains(PASSWORD_KEY);
}

function clearCredentials() {
  if (Keychain.contains(USERNAME_KEY)) Keychain.remove(USERNAME_KEY);
  if (Keychain.contains(PASSWORD_KEY)) Keychain.remove(PASSWORD_KEY);
}

async function setupCredentials() {
  const alert = new Alert();
  alert.title = "SEU WLAN";
  alert.message = "保存校园网账号。";
  alert.addTextField(
    "一卡通号",
    Keychain.contains(USERNAME_KEY) ? Keychain.get(USERNAME_KEY) : ""
  );
  alert.addSecureTextField("校园网密码", "");
  alert.addAction("保存");
  alert.addCancelAction("取消");

  const selected = await alert.presentAlert();
  if (selected < 0) throw new Error("已取消配置");

  const username = alert.textFieldValue(0).trim();
  const password = alert.textFieldValue(1);
  if (!username || !password) throw new Error("一卡通号和密码不能为空");

  Keychain.set(USERNAME_KEY, username);
  Keychain.set(PASSWORD_KEY, password);
}

async function credentials() {
  if (!hasCredentials()) await setupCredentials();
  return {
    username: Keychain.get(USERNAME_KEY),
    password: Keychain.get(PASSWORD_KEY),
  };
}

async function status() {
  const data = parseJsonp(await getText(STATUS_URL));
  const result = String(data.result ?? "");
  const ip = String(data.v46ip || data.v4ip || data.ss5 || "");
  if (result !== "0" && result !== "1") {
    throw new Error("认证网关返回未知状态: " + result);
  }
  return { authenticated: result === "1", ip };
}

async function login(username, password, ip) {
  if (!ip) throw new Error("未获取到校园网 IP");

  const params = [
    "c=Portal",
    "a=login",
    "callback=dr1003",
    "login_method=1",
    "user_account=" + encodeURIComponent(",0," + username),
    "user_password=" + encodeURIComponent(password),
    "wlan_user_ip=" + encodeURIComponent(ip),
  ].join("&");

  const data = parseJsonp(await getText(LOGIN_URL + "?" + params));
  if (String(data.result ?? "") !== "1") {
    throw new Error("认证失败，请检查账号密码");
  }
}

async function authenticate() {
  const saved = await credentials();
  const current = await status();

  if (current.authenticated) return "SEU WLAN 已认证";

  await login(saved.username, saved.password, current.ip);
  const verified = await status();
  if (!verified.authenticated) {
    throw new Error("网关返回登录成功，但状态复核仍未认证");
  }

  return "SEU WLAN 认证成功";
}

async function appMenu() {
  if (!hasCredentials()) {
    await setupCredentials();
    return await authenticate();
  }

  const menu = new Alert();
  menu.title = "SEU WLAN";
  menu.message = "选择操作";
  menu.addAction("立即认证");
  menu.addAction("重新配置账号");
  menu.addDestructiveAction("清除凭据");
  menu.addCancelAction("取消");

  const selected = await menu.presentSheet();
  if (selected === 0) return await authenticate();
  if (selected === 1) {
    await setupCredentials();
    return "账号已更新";
  }
  if (selected === 2) {
    clearCredentials();
    return "本机凭据已清除";
  }
  return "已取消";
}

async function main() {
  const parameter = String(args.shortcutParameter ?? "").trim().toLowerCase();

  if (parameter === "setup") {
    await setupCredentials();
    return "账号已更新";
  }
  if (parameter === "forget") {
    clearCredentials();
    return "本机凭据已清除";
  }

  if (config.runsInApp) return await appMenu();
  return await authenticate();
}

try {
  const result = await main();
  Script.setShortcutOutput(result);
  console.log(result);
} catch (error) {
  const message = "SEU WLAN: " + String(error);
  Script.setShortcutOutput(message);
  console.error(message);
}

Script.complete();
