export default class APIClient {
  constructor() {
    this.apiVersion = 'v1';
  }

  getUrl(url) {
    return `/api/${this.apiVersion}/${url}/`;
  }

  request(url, data, options) {
    const defaults = {
      url: this.getUrl(url),
      data,
      contentType: 'application/json',
      dataType: 'json',
      // Browser will automatically send sessionid cookie because it is marked as httponly
      headers: {},
      // 30 seconds
      timeout: 30000,
    };
    return $.ajax($.extend(defaults, options));
  }

  get(url, data = {}) {
    return this.request(url, data, { method: 'GET' });
  }

  post(url, data = {}) {
    return this.request(url, data, { method: 'POST' });
  }

  put(url, data = {}) {
    return this.request(url, data, { method: 'PUT' });
  }

  patch(url, data = {}) {
    return this.request(url, data, { method: 'PATCH' });
  }

  delete(url) {
    return this.request(url, {}, { method: 'DELETE' });
  }
}

// Uncomment the next line to make this a singleton
// export default new APIClient();
