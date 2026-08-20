from toontown.town import Street


class DLStreet(Street.Street):

    def enter(self, requestStatus):
        Street.Street.enter(self, requestStatus)
        render.setColorScale(Vec4(.55, .55, .65, 1))

    def exit(self):
        Street.Street.exit(self)
        render.setColorScale(Vec4(1, 1, 1, 1))
