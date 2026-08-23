from main import app
# Vercel needs this
def handler(request):
    return app(request)
