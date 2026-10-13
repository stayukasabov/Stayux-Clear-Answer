A CDN is a network of servers placed in many places around the world. It keeps copies of your content close to your users. This makes pages load faster and lowers the load on your main server.

## The parts

- The origin server holds the original content of the site.
- The edge servers are the CDN computers that sit near users and store copies of the content.
- The cache on each edge server holds the saved files, such as images, scripts, and videos.
- The DNS or routing system sends each user to a nearby edge server.
- The cache rules tell an edge server how long it may keep a file.

## The steps

1. A user asks for a page or a file.
2. The DNS or routing system sends the request to the closest edge server.
3. The edge server checks its cache for the file.
4. If the file is there and still fresh, the edge server sends it to the user.
5. If the file is not there, the edge server asks the origin server for it.
6. The edge server saves a copy and sends the file to the user.
7. The next user nearby gets the saved copy, and the origin is not used.

## Limits

A CDN works best for content that does not change often. Private or fast-changing content is hard to cache. Old copies can reach users until the cache rules expire them or you purge them. The first request for a file is still slow, because it must go to the origin.