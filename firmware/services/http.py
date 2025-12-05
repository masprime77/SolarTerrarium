try:
    import urequests as requests
except ImportError:
    import requests

def http_get_json(url, timeout=10):
    r = None
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code != 200:
            raise RuntimeError("HTTP %d" % r.status_code)
        data = r.json()
        return data
    
    except Exception as e:
        print(f"HTTP GET error: {e}")
        return None

    finally:
        try:
            if r:
                r.close()
        except:
            pass