require "kemal"
require "kemal-session"
require "uuid"
require "http/params"

OAUTH_URL    = ENV["OAUTH_SERVER_URL"]
REDIRECT_URL = "https://login.threefold.me"

Dir.mkdir_p("data")
Kemal::Session.config do |config|
  config.engine = Kemal::Session::FileEngine.new({:sessions_dir => "./data"})
  config.secret = "some_secret"
end

get "/start" do |env|
  state = UUID.random.to_s.gsub('-', "")
  #   state = "034e0b4adae941b4b6440695c3c5774b"
  env.session.string("state", state)
  res = HTTP::Client.get "#{OAUTH_URL}/pubkey"
  if !res.success?
    env.response.status_code = 500
    env.response.print "Unexpected error while contacting Oauth server, error code was #{res.status_code}"
  end
  data = JSON.parse(res.body)
  data["publickey"].to_s
  params = {
    "state":       state,
    "appid":       env.request.headers["host"],
    "scope":       {"user": true, "email": true}.to_json,
    "redirecturl": "/callback",
    "publickey":   data["publickey"].to_s,
  }
  params = HTTP::Params.encode(params)
  env.redirect "#{REDIRECT_URL}?#{params}"
end

get "/callback" do |env|
  data = env.params.query["signedAttempt"]
  state = env.session.string?("state") || ""
  #   state = "034e0b4adae941b4b6440695c3c5774b"
  res = HTTP::Client.post("#{OAUTH_URL}/verify", form: {"signedAttempt" => data, "state" => state})
  if !res.success?
    env.response.status_code = res.status_code
    env.response.print res.status_message
  end
  res.body
end
Kemal.run
