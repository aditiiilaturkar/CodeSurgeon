# Testing Nginx uwsgi caching
This README walks through how to build Nginx and run it as a web server for a uwsgi application server. There are two included configurations which enable and disable uwsgi caching.

The Nginx module which implements uwsgi support is [ngx_http_uwsgi_module](https://nginx.org/en/docs/http/ngx_http_uwsgi_module.html). 

## Build Nginx
```
curl -OL https://github.com/nginx/nginx/archive/refs/tags/release-1.25.2.tar.gz
tar -xzf release-1.25.2.tar.gz
cd nginx-release-1.25.2
# build without http_rewrite_module to avoid another dependency
./auto/configure --without-http_rewrite_module
make
```

## Setup
- Install python dependencies
```
pip install uwsgi
```
- Set up Nginx directories
```
export NGINX_PREFIX='nginx_data_files_dir'
mkdir "$NGINX_PREFIX/cache"
mkdir "$NGINX_PREFIX/logs"
```
- Copy `uwsgi_params` to same directory as nginx.conf files
```
cp nginx_source_dir/conf/uwsgi_params .
```

## Running
- Select an nginx.conf:
- `nginx-cache.conf` - uwsgi caching enabled, will exercise the target feature
- `nginx-no-cache.conf` - uwsgi caching disabled

- Start the nginx and uwsgi servers
```
# start nginx
nginx -p $NGINX_PREFIX -c /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-cache.conf 
# start uwsgi server
uwsgi --socket 127.0.0.1:9000 --wsgi-file server.py
```
- Now send requests to nginx:
```
# expected response is "Hello world"
curl -X GET localhost:80/ 
# Vary request URI (the cache's key), which should cause cache misses
curl -X GET localhost:80/path1
curl -X GET localhost:80/path2
curl -X GET localhost:80/path3
```

<!-- sudo /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-release-1.25.2/objs/nginx -p /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx_data_files_dir/ -c /home/aditi/CodeSurgeon/test-nginx-uwsgi/nginx-cache.conf   -->