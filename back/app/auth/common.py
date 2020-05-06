class Common:
    def truereturn(self, data, msg):
        return {
            "status": True,
            "data": data,
            "msg": msg
        }

    def falsereturn(self, data, msg):
        return {
            "status": False,
            "data": data,
            "msg": msg
        }

common = Common()
